"""Read-only HTTP/MJPEG continuity check; no capture, ACK or movement."""
import argparse
import json
from pathlib import Path
from time import monotonic
import requests
from app.config import load_config


def check(host, control_port=80, stream_port=81, seconds=30, timeout=2):
    session = requests.Session()
    session.trust_env = False
    errors, samples = [], []
    frames = total_bytes = 0
    max_gap = 0.0
    status = None
    began = monotonic()
    try:
        start = monotonic()
        try:
            response = session.get(f'http://{host}:{control_port}/status', timeout=timeout)
            response.raise_for_status()
            status = response.json()
            samples.append(dict(endpoint='status',elapsed_s=round(monotonic()-start,3),ok=True))
        except (requests.RequestException, ValueError) as error:
            errors.append(str(error))
            samples.append(dict(endpoint='status',ok=False))
        with session.get(f'http://{host}:{stream_port}/stream',stream=True,timeout=(timeout,timeout)) as response:
            response.raise_for_status()
            buffer = b''
            last = monotonic()
            start = last
            for chunk in response.iter_content(4096):
                now = monotonic()
                max_gap = max(max_gap, now-last)
                last = now
                total_bytes += len(chunk)
                buffer += chunk
                while True:
                    first = buffer.find(b'\xff\xd8')
                    end = buffer.find(b'\xff\xd9',first+2) if first >= 0 else -1
                    if end < 0:
                        break
                    frames += 1
                    buffer = buffer[end+2:]
                if len(buffer) > 2*1024*1024:
                    raise ValueError('MJPEG buffer exceeds2MB without complete JPEG')
                if now-start >= seconds:
                    break
    except (requests.RequestException, ValueError) as error:
        errors.append(str(error))
    finally:
        session.close()
    duration = monotonic()-began
    return dict(camera_host=host,frames=frames,bytes=total_bytes,elapsed_s=round(duration,3),
                received_fps=round(frames/duration,2) if duration else 0,
                max_chunk_gap_s=round(max_gap,3),status=status,requests=samples,
                errors=errors,ok=status is not None and frames>0 and not errors)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='config.phase5.yaml')
    parser.add_argument('--seconds',type=float,default=30)
    parser.add_argument('--report',type=Path,default=Path('logs/phase5-network-unoq.json'))
    args=parser.parse_args()
    if args.seconds <= 0: parser.error('--seconds must be positive')
    config=load_config(args.config)
    report=check(config.s3_ip,config.camera_http_port,config.camera_stream_port,args.seconds)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)
    return 0 if report['ok'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
