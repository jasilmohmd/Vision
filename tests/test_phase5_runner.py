import os
from pathlib import Path
import shutil
import subprocess
import pytest


def bash_binary():
    git_bash=Path('C:/Program Files/Git/bin/bash.exe')
    if os.name=='nt':
        if git_bash.exists():return str(git_bash)
        pytest.skip('Git Bash needed for Linux launcher test on Windows')
    path=shutil.which('bash')
    if not path:pytest.skip('Bash not installed')
    return path


@pytest.mark.parametrize('pgrep_status,expected',[(0,2),(1,0),(2,2)])
def test_guard_pattern_is_one_argument_and_failures_stop_app(tmp_path,pgrep_status,expected):
    (tmp_path/'deploy').mkdir()
    shutil.copyfile(Path('deploy/run_phase5.sh'),tmp_path/'deploy/run_phase5.sh')
    (tmp_path/'fakebin').mkdir()
    (tmp_path/'.venv/bin').mkdir(parents=True)
    pgrep=tmp_path/'fakebin/pgrep'
    pgrep.write_text('#!/usr/bin/env bash\nprintf "%s\n" "$#" > pgrep-count\nprintf "%s\n" "$2" > pgrep-pattern\nexit "$TEST_PGREP_STATUS"\n')
    pgrep.chmod(0o755)
    python=tmp_path/'.venv/bin/python'
    python.write_text('#!/usr/bin/env bash\nprintf "%s " "$@"\n')
    python.chmod(0o755)
    env=dict(os.environ,TEST_PGREP_STATUS=str(pgrep_status))
    result=subprocess.run([bash_binary(),'-c','export PATH="$PWD/fakebin:$PATH"; bash deploy/run_phase5.sh live'],cwd=tmp_path,env=env,capture_output=True,text=True)
    assert result.returncode==expected,(result.stdout,result.stderr)
    assert (tmp_path/'pgrep-count').read_text().strip()=='2'
    assert (tmp_path/'pgrep-pattern').read_text().strip()==r'[p]ython.*-m app\.main'
    if pgrep_status==1:assert '-m app.main' in result.stdout
    else:assert '-m app.main' not in result.stdout
