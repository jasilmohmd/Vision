"""Fetch official YuNet and small English Vosk models (also works on Windows)."""
import argparse
from pathlib import Path
import urllib.request
import zipfile

YUNET_URL = 'https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx'
VOSK_URL = 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'


def download(url, destination):
    temporary = destination.with_suffix(destination.suffix + '.part')
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temporary.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path('models'))
    args = parser.parse_args()
    directory = args.output_dir.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    face = directory / 'face_detection_yunet_2023mar.onnx'
    if not face.exists():
        print('Downloading YuNet...', flush=True)
        download(YUNET_URL, face)
    vosk = directory / 'vosk-model-small-en-us-0.15'
    if not (vosk / 'am' / 'final.mdl').is_file():
        archive_path = directory / 'vosk-model-small-en-us-0.15.zip'
        print('Downloading Vosk small English...', flush=True)
        download(VOSK_URL, archive_path)
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                if not (directory / member.filename).resolve().is_relative_to(directory):
                    raise ValueError('Unsafe archive path')
            archive.extractall(directory)
        archive_path.unlink()
    print(f'Models ready: {directory}')


if __name__ == '__main__':
    main()
