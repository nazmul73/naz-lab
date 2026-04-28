# Naz Lab Phase 1 Text Workstation — One-Cell Colab Launcher

Use this in one Python cell in Google Colab.

This launcher:

- mounts Google Drive
- uses `/content/drive/MyDrive/NazLab/` for persistent storage
- clones or updates the latest repo
- creates the required Drive folder structure
- installs Streamlit and requests
- installs Ollama with a robust fallback path
- links Ollama models to Drive so models persist across sessions
- starts Ollama
- pulls a safe CPU fallback model and optional Gemma model
- validates `text_workstation/app.py`
- launches the Text Workstation with a Colab proxy window

```python
# @title 🚀 Naz Lab Phase 1: Text Workstation One-Cell Launcher
import os
import shutil
import subprocess
import time
from pathlib import Path
from google.colab import drive, output

REPO_URL = "https://github.com/nazmul73/naz-lab.git"
REPO_DIR = Path("/content/naz-lab")
BASE_PATH = Path("/content/drive/MyDrive/NazLab")
APP_REL = "text_workstation/app.py"
PORT = 8501
LOG_PATH = Path("/content/streamlit_text_workstation_phase1.log")
OLLAMA_INSTALL_LOG = Path("/content/ollama_install_phase1.log")

print("============================================================")
print("Naz Lab Phase 1 Text Workstation Launcher")
print("============================================================")

# 1. Mount Drive
if not Path("/content/drive/MyDrive").exists():
    print("Mounting Google Drive...")
    drive.mount("/content/drive")

if not Path("/content/drive/MyDrive").exists():
    raise RuntimeError("Google Drive is not mounted. Please authorize Drive mount and run again.")

# 2. Clone or update repo
os.chdir("/content")
if (REPO_DIR / ".git").exists():
    print("Updating existing repo...")
    os.chdir(REPO_DIR)
    subprocess.run(["git", "fetch", "--depth", "1", "origin", "main"], check=True)
    subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
else:
    print("Cloning repo...")
    if REPO_DIR.exists():
        subprocess.run(["rm", "-rf", str(REPO_DIR)], check=True)
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)], check=True)
    os.chdir(REPO_DIR)

print("Latest commit:")
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

# 4. Install dependencies
print("Installing Python dependencies...")
subprocess.run(["python", "-m", "pip", "install", "-q", "streamlit", "requests"], check=True)

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

    print("Official Ollama install failed. Trying direct Linux amd64 tarball fallback...")
    fallback_cmd = " && ".join([
        "cd /content",
        "rm -f ollama-linux-amd64.tgz",
        "curl -fL https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz",
        "tar -C /usr -xzf ollama-linux-amd64.tgz",
        "chmod +x /usr/bin/ollama /usr/local/bin/ollama 2>/dev/null || true",
    ])
    fallback = run_logged(fallback_cmd, check=False)
    if fallback.returncode == 0 and ollama_exists():
        print("Ollama installed with direct tarball fallback.")
        return True

    print("Ollama install failed. Install log tail:")
    print(OLLAMA_INSTALL_LOG.read_text(encoding="utf-8", errors="ignore")[-4000:])
    return False

if not install_ollama():
    raise RuntimeError(
        "Ollama installation failed. See /content/ollama_install_phase1.log. "
        "This is an environment/network install failure before the app launch step."
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
    ollama_proc = subprocess.Popen(["ollama", "serve"], stdout=log_file, stderr=subprocess.STDOUT)

time.sleep(8)
print("Ollama log tail:")
print(ollama_log.read_text(encoding="utf-8", errors="ignore")[-1500:])

# 8. Pull models. qwen is CPU-safe; gemma2 is the requested persistent Gemma model.
print("Pulling CPU fallback model qwen2.5:0.5b...")
qwen_result = subprocess.run(["ollama", "pull", "qwen2.5:0.5b"], check=False)
if qwen_result.returncode != 0:
    print("qwen2.5:0.5b pull failed. The app can launch, but generation will need a model installed.")

print("Pulling Gemma model gemma2:2b if runtime allows...")
gemma_result = subprocess.run(["ollama", "pull", "gemma2:2b"], check=False)
if gemma_result.returncode != 0:
    print("Gemma pull did not complete. You can still use qwen2.5:0.5b if it installed successfully.")

print("Installed Ollama models:")
subprocess.run(["ollama", "list"], check=False)

# 9. Validate app
print("Validating Text Workstation app...")
subprocess.run(["python", "-m", "py_compile", str(REPO_DIR / APP_REL)], check=True)

# 10. Stop old Streamlit and launch app
print("Stopping old Streamlit...")
subprocess.run("pkill -f streamlit || true", shell=True, check=False)
time.sleep(2)

print("Starting Text Workstation on port", PORT)
with LOG_PATH.open("w", encoding="utf-8") as log_file:
    process = subprocess.Popen(
        [
            "python", "-m", "streamlit", "run", str(REPO_DIR / APP_REL),
            "--server.port", str(PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
        ],
        stdout=log_file,
        stderr=subprocess.STDOUT,
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
Drive structure ready: /content/drive/MyDrive/NazLab
Ollama installed with official script.
# or
Ollama installed with direct tarball fallback.
Ollama models path: /root/.ollama/models -> /content/drive/MyDrive/NazLab/models/ollama
Installed Ollama models:
...
Validating Text Workstation app...
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
