# Naz Lab Phase 1 Text Workstation — One-Cell Colab Launcher

Use this in one Python cell in Google Colab.

This launcher:

- mounts Google Drive
- uses `/content/drive/MyDrive/NazLab/` for persistent storage
- supports existing ZIP-based repo at `/content/naz-lab`
- creates the required Drive folder structure
- checks/installs Streamlit with a logged resilient pip flow
- installs system dependency `zstd` required by current Ollama releases
- installs Ollama
- links Ollama models to Drive so models persist across sessions
- starts Ollama
- pulls a safe CPU fallback model and optional Gemma model
- validates `text_workstation/app.py`
- launches the Text Workstation from a stable working directory
- opens the app with Colab proxy

```python
# @title 🚀 Naz Lab Phase 1: Text Workstation One-Cell Launcher
import importlib.util
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from google.colab import drive, output

REPO_URL = "https://github.com/nazmul73/naz-lab.git"
REPO_DIR = Path("/content/naz-lab")
BASE_PATH = Path("/content/drive/MyDrive/NazLab")
APP_REL = "text_workstation/app.py"
PORT = 8501
LOG_PATH = Path("/content/streamlit_text_workstation_phase1.log")
PIP_LOG_PATH = Path("/content/pip_phase1.log")
OLLAMA_INSTALL_LOG = Path("/content/ollama_install_phase1.log")

print("============================================================")
print("Naz Lab Phase 1 Text Workstation Launcher")
print("============================================================")

# 1. Mount Drive
os.chdir("/content")
if not Path("/content/drive/MyDrive").exists():
    print("Mounting Google Drive...")
    drive.mount("/content/drive")

if not Path("/content/drive/MyDrive").exists():
    raise RuntimeError("Google Drive is not mounted. Please authorize Drive mount and run again.")

# 2. Locate repo. Prefer existing ZIP-based repo when git is broken in Colab.
os.chdir("/content")
if REPO_DIR.exists() and (REPO_DIR / APP_REL).exists():
    print("Using repo at", REPO_DIR)
elif (REPO_DIR / ".git").exists():
    print("Updating existing git repo...")
    os.chdir(REPO_DIR)
    subprocess.run(["git", "fetch", "--depth", "1", "origin", "main"], check=False)
    subprocess.run(["git", "reset", "--hard", "origin/main"], check=False)
elif not REPO_DIR.exists():
    print("Cloning repo...")
    clone_result = subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)], check=False)
    if clone_result.returncode != 0:
        raise RuntimeError("Git clone failed. Use ZIP fallback repo download first, then run this launcher again.")
else:
    raise RuntimeError(f"Repo folder exists but app is missing: {REPO_DIR / APP_REL}")

if not (REPO_DIR / APP_REL).exists():
    raise RuntimeError(f"Required app not found: {REPO_DIR / APP_REL}")

os.chdir(REPO_DIR)
print("Stable working directory:", os.getcwd())
print("Latest commit if git metadata is available:")
subprocess.run(["git", "log", "-1", "--oneline"], check=False)

# 3. Create persistent Naz Lab Drive structure
required_dirs = [
    BASE_PATH,
    BASE_PATH / "text_outputs",
    BASE_PATH / "chat_outputs",
    BASE_PATH / "script_outputs",
    BASE_PATH / "image_prompts",
    BASE_PATH / "image_outputs",
    BASE_PATH / "voice_outputs",
    BASE_PATH / "video_outputs",
    BASE_PATH / "job_queue",
    BASE_PATH / "job_queue" / "image_jobs",
    BASE_PATH / "job_queue" / "voice_jobs",
    BASE_PATH / "job_queue" / "video_jobs",
    BASE_PATH / "job_queue" / "completed_jobs",
    BASE_PATH / "models",
    BASE_PATH / "models" / "ollama",
    BASE_PATH / "config",
    BASE_PATH / "logs",
    BASE_PATH / "temp",
]
for folder in required_dirs:
    folder.mkdir(parents=True, exist_ok=True)

json_defaults = {
    BASE_PATH / "config" / "workstation_links.json": "{}",
    BASE_PATH / "config" / "custom_gems.json": "{}",
    BASE_PATH / "config" / "tool_links.json": "{}",
    BASE_PATH / "logs" / "output_log.json": '{"logs": []}',
}
for file_path, default_text in json_defaults.items():
    if not file_path.exists():
        file_path.write_text(default_text, encoding="utf-8")

print("Drive structure ready:", BASE_PATH)

# 4. Python dependency handling
def module_exists(name):
    return importlib.util.find_spec(name) is not None


def run_pip(command):
    print("Running pip:", " ".join(command))
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    with PIP_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write("\n$ " + " ".join(command) + "\n")
        handle.write(result.stdout or "")
        handle.write(f"\n[exit_code={result.returncode}]\n")
    return result

PIP_LOG_PATH.write_text("Naz Lab Phase 1 pip log\n", encoding="utf-8")

if module_exists("streamlit"):
    print("Streamlit already installed.")
else:
    print("Installing Streamlit...")
    pip_attempts = [
        [sys.executable, "-m", "pip", "install", "-q", "streamlit"],
        [sys.executable, "-m", "pip", "install", "--break-system-packages", "-q", "streamlit"],
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", "-q", "streamlit"],
    ]
    installed = False
    for cmd in pip_attempts:
        result = run_pip(cmd)
        if result.returncode == 0 and module_exists("streamlit"):
            installed = True
            break
    if not installed:
        print("Streamlit install failed. Pip log tail:")
        print(PIP_LOG_PATH.read_text(encoding="utf-8", errors="ignore")[-4000:])
        raise RuntimeError("Streamlit is not installed and pip install failed. See /content/pip_phase1.log")

print("Streamlit import check OK.")

print("Installing system dependency zstd for Ollama extraction...")
subprocess.run("apt-get update -qq && apt-get install -y -qq zstd", shell=True, check=True)

# 5. Robust Ollama install helpers
def run_logged(command, *, check=False):
    print("Running:", command)
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    with OLLAMA_INSTALL_LOG.open("a", encoding="utf-8") as handle:
        handle.write("\n$ " + command + "\n")
        handle.write(result.stdout or "")
        handle.write(f"\n[exit_code={result.returncode}]\n")
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout)
    return result


def ollama_exists():
    return shutil.which("ollama") is not None or Path("/usr/local/bin/ollama").exists() or Path("/usr/bin/ollama").exists()


def install_ollama():
    if ollama_exists():
        print("Ollama already installed.")
        return True

    OLLAMA_INSTALL_LOG.write_text("Naz Lab Ollama install log\n", encoding="utf-8")
    print("Installing Ollama with official install script...")
    official = run_logged("curl -fsSL https://ollama.com/install.sh | sh", check=False)
    if official.returncode == 0 and ollama_exists():
        print("Ollama installed with official script.")
        return True

    print("Official Ollama install failed after zstd install. Install log tail:")
    print(OLLAMA_INSTALL_LOG.read_text(encoding="utf-8", errors="ignore")[-4000:])
    return False

if not install_ollama():
    raise RuntimeError(
        "Ollama installation failed even after installing zstd. See /content/ollama_install_phase1.log."
    )

print("Ollama binary:")
subprocess.run("which ollama && ollama --version", shell=True, check=False)

# 6. Link Ollama model directory to Drive persistence
print("Configuring Ollama model persistence...")
Path("/root/.ollama").mkdir(parents=True, exist_ok=True)
ollama_models_link = Path("/root/.ollama/models")
drive_ollama_models = BASE_PATH / "models" / "ollama"
drive_ollama_models.mkdir(parents=True, exist_ok=True)

if ollama_models_link.exists() or ollama_models_link.is_symlink():
    if ollama_models_link.is_symlink():
        if ollama_models_link.resolve() != drive_ollama_models.resolve():
            ollama_models_link.unlink()
            os.symlink(str(drive_ollama_models), str(ollama_models_link))
    else:
        subprocess.run(["rm", "-rf", str(ollama_models_link)], check=True)
        os.symlink(str(drive_ollama_models), str(ollama_models_link))
else:
    os.symlink(str(drive_ollama_models), str(ollama_models_link))

print("Ollama models path:", ollama_models_link, "->", drive_ollama_models)

# 7. Start Ollama server
print("Starting Ollama server...")
subprocess.run("pkill -f 'ollama serve' || true", shell=True, check=False)
time.sleep(2)
ollama_log = Path("/content/ollama_phase1.log")
with ollama_log.open("w", encoding="utf-8") as log_file:
    ollama_proc = subprocess.Popen(["ollama", "serve"], stdout=log_file, stderr=subprocess.STDOUT, cwd=str(REPO_DIR))

time.sleep(8)
print("Ollama log tail:")
print(ollama_log.read_text(encoding="utf-8", errors="ignore")[-1500:])

# 8. Pull models. qwen is CPU-safe; gemma2 is the requested persistent Gemma model.
print("Pulling CPU fallback model qwen2.5:0.5b...")
qwen_result = subprocess.run(["ollama", "pull", "qwen2.5:0.5b"], check=False, cwd=str(REPO_DIR))
if qwen_result.returncode != 0:
    print("qwen2.5:0.5b pull failed. The app can launch, but generation will need a model installed.")

print("Pulling Gemma model gemma2:2b if runtime allows...")
gemma_result = subprocess.run(["ollama", "pull", "gemma2:2b"], check=False, cwd=str(REPO_DIR))
if gemma_result.returncode != 0:
    print("Gemma pull did not complete. You can still use qwen2.5:0.5b if it installed successfully.")

print("Installed Ollama models:")
subprocess.run(["ollama", "list"], check=False, cwd=str(REPO_DIR))

# 9. Validate app
print("Validating Text Workstation app...")
os.chdir(REPO_DIR)
subprocess.run([sys.executable, "-m", "py_compile", str(REPO_DIR / APP_REL)], check=True, cwd=str(REPO_DIR))

# 10. Stop old Streamlit and launch app
print("Stopping old Streamlit...")
subprocess.run("pkill -f streamlit || true", shell=True, check=False, cwd=str(REPO_DIR))
time.sleep(2)

print("Starting Text Workstation on port", PORT)
os.chdir(REPO_DIR)
print("Launch cwd:", os.getcwd())
with LOG_PATH.open("w", encoding="utf-8") as log_file:
    process = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", str(REPO_DIR / APP_REL),
            "--server.port", str(PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
        ],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=str(REPO_DIR),
    )

time.sleep(8)

print("Streamlit log:")
print(LOG_PATH.read_text(encoding="utf-8", errors="ignore")[-3000:])

if process.poll() is not None:
    raise RuntimeError(f"Text Workstation exited early. Check log: {LOG_PATH}")

print("============================================================")
print("NAZ LAB PHASE 1 TEXT WORKSTATION READY")
print("Expected app features:")
print("- General Chat")
print("- Free Writer / Story Writer / Viral Script Writer / Caption Writer / Prompt Improver")
print("- Save text outputs to Drive")
print("- Prompt Improver creates Image Job JSON in job_queue/image_jobs")
print("- Ollama model persistence linked to Drive")
print("Opening Colab proxy window...")
print("============================================================")

output.serve_kernel_port_as_window(PORT)
```

## Expected output

```text
Naz Lab Phase 1 Text Workstation Launcher
Stable working directory: /content/naz-lab
Drive structure ready: /content/drive/MyDrive/NazLab
Streamlit already installed.
# or
Streamlit import check OK.
Installing system dependency zstd for Ollama extraction...
Ollama installed with official script.
Ollama models path: /root/.ollama/models -> /content/drive/MyDrive/NazLab/models/ollama
Installed Ollama models:
...
Validating Text Workstation app...
Launch cwd: /content/naz-lab
Starting Text Workstation on port 8501
NAZ LAB PHASE 1 TEXT WORKSTATION READY
Opening Colab proxy window...
```

## First test checklist

Only the UI test must be done manually in Colab:

```text
1. Open Text Workstation
2. Select qwen2.5:0.5b if using CPU, or gemma2:2b if using GPU
3. Test Free Writer or Story Writer
4. Test Prompt Improver
5. Confirm a .txt output is saved
6. Confirm an image_job_*.json file appears in /content/drive/MyDrive/NazLab/job_queue/image_jobs/
```
