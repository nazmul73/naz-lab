"""Colab launcher for Naz Lab Text Workstation Phase 1.10.

Run with:
python /content/naz-lab/launchers/phase1_10_text_workstation_colab.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_DIR = Path('/content/naz-lab')
BASE_PATH = Path('/content/drive/MyDrive/NazLab')
APP_REL = 'text_workstation/app_phase110.py'
PORT = 8501
LOG_PATH = Path('/content/streamlit_text_workstation_phase110.log')


def run(cmd: list[str] | str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=isinstance(cmd, str), check=check)


def ensure_dirs() -> None:
    dirs = [
        BASE_PATH,
        BASE_PATH / 'text_outputs',
        BASE_PATH / 'chat_outputs',
        BASE_PATH / 'script_outputs',
        BASE_PATH / 'image_prompts',
        BASE_PATH / 'image_outputs',
        BASE_PATH / 'voice_outputs',
        BASE_PATH / 'video_outputs',
        BASE_PATH / 'job_queue' / 'image_jobs',
        BASE_PATH / 'job_queue' / 'voice_jobs',
        BASE_PATH / 'job_queue' / 'video_jobs',
        BASE_PATH / 'job_queue' / 'completed_jobs',
        BASE_PATH / 'models' / 'ollama',
        BASE_PATH / 'config',
        BASE_PATH / 'logs',
        BASE_PATH / 'temp',
    ]
    for folder in dirs:
        folder.mkdir(parents=True, exist_ok=True)
    defaults = {
        BASE_PATH / 'config' / 'workstation_links.json': '{}',
        BASE_PATH / 'config' / 'custom_gems.json': '{}',
        BASE_PATH / 'config' / 'tool_links.json': '{}',
        BASE_PATH / 'logs' / 'output_log.json': '{"logs": []}',
    }
    for path, text in defaults.items():
        if not path.exists():
            path.write_text(text, encoding='utf-8')


def main() -> None:
    if not (REPO_DIR / APP_REL).exists():
        raise RuntimeError(f'Missing app: {REPO_DIR / APP_REL}')
    os.chdir(REPO_DIR)
    ensure_dirs()
    run([sys.executable, '-m', 'pip', 'install', '-q', 'streamlit', 'requests'], check=False)
    run('apt-get update -qq && apt-get install -y -qq zstd', check=True)
    if not Path('/usr/local/bin/ollama').exists() and not Path('/usr/bin/ollama').exists():
        run('curl -fsSL https://ollama.com/install.sh | sh', check=True)
    Path('/root/.ollama').mkdir(parents=True, exist_ok=True)
    model_link = Path('/root/.ollama/models')
    drive_models = BASE_PATH / 'models' / 'ollama'
    if model_link.exists() or model_link.is_symlink():
        run(['rm', '-rf', str(model_link)], check=True)
    os.symlink(str(drive_models), str(model_link))
    run("pkill -f 'ollama serve' || true", check=False)
    time.sleep(2)
    with Path('/content/ollama_phase110.log').open('w', encoding='utf-8') as log:
        subprocess.Popen(['ollama', 'serve'], stdout=log, stderr=subprocess.STDOUT, cwd=str(REPO_DIR))
    time.sleep(8)
    run(['ollama', 'pull', 'qwen2.5:1.5b'], check=False)
    run(['ollama', 'pull', 'qwen2.5:0.5b'], check=False)
    run([sys.executable, '-m', 'py_compile', str(REPO_DIR / APP_REL)], check=True)
    run('pkill -f streamlit || true', check=False)
    time.sleep(2)
    with LOG_PATH.open('w', encoding='utf-8') as log:
        subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', str(REPO_DIR / APP_REL),
            '--server.port', str(PORT),
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--server.enableCORS', 'false',
            '--server.enableXsrfProtection', 'false',
        ], stdout=log, stderr=subprocess.STDOUT, cwd=str(REPO_DIR))
    time.sleep(8)
    print(LOG_PATH.read_text(encoding='utf-8', errors='ignore')[-2000:])
    print('NAZ LAB PHASE 1.10 TEXT WORKSTATION READY')


if __name__ == '__main__':
    main()
