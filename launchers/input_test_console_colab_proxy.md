# Naz Lab Input Test Console Colab Proxy Launcher

Use this launcher when Cloudflare tunnel creates a link but the browser cannot open the site.

This uses Colab's built-in authenticated proxy instead of Cloudflare.

## Colab cell

Run this in a Python cell, not a Bash cell.

```python
import os
import subprocess
import time
from pathlib import Path
from google.colab import output

REPO_URL = "https://github.com/nazmul73/naz-lab.git"
REPO_DIR = Path("/content/naz-lab")
APP_REL = "test_console/app.py"
PORT = 8508
LOG_PATH = Path("/content/streamlit_test_console_proxy.log")

print("============================================================")
print("Naz Lab Input Test Console - Colab Proxy Launcher")
print("============================================================")

if not Path("/content/drive/MyDrive").exists():
    raise RuntimeError("Google Drive is not mounted. Run: from google.colab import drive; drive.mount('/content/drive')")

os.chdir("/content")
if (REPO_DIR / ".git").exists():
    os.chdir(REPO_DIR)
    subprocess.run(["git", "fetch", "--depth", "1", "origin", "main"], check=True)
    subprocess.run(["git", "reset", "--hard", "origin/main"], check=True)
else:
    if REPO_DIR.exists():
        subprocess.run(["rm", "-rf", str(REPO_DIR)], check=True)
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(REPO_DIR)], check=True)
    os.chdir(REPO_DIR)

subprocess.run(["git", "log", "-1", "--oneline"], check=False)

print("Installing Streamlit...")
subprocess.run(["python", "-m", "pip", "install", "-q", "streamlit"], check=True)

print("Validating app...")
subprocess.run(["python", "-m", "py_compile", str(REPO_DIR / APP_REL)], check=True)

print("Stopping old Streamlit processes...")
subprocess.run("pkill -f streamlit || true", shell=True, check=False)
time.sleep(2)

print("Starting Input Test Console on port", PORT)
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
print("Streamlit log tail:")
print(LOG_PATH.read_text(encoding="utf-8", errors="ignore")[-3000:])

if process.poll() is not None:
    raise RuntimeError(f"Streamlit exited early. Check log: {LOG_PATH}")

print("============================================================")
print("NAZ LAB INPUT TEST CONSOLE READY")
print("Opening Colab proxy window...")
print("If it does not open automatically, use the displayed proxy link/output.")
print("============================================================")

output.serve_kernel_port_as_window(PORT)
```

## Why this launcher exists

Cloudflare quick tunnel may sometimes create a URL that is not reachable from the browser because of DNS/tunnel propagation or network issues.

This launcher avoids Cloudflare and uses Colab's own port proxy.

## Expected result

A new Colab proxy browser window should open with:

```text
Naz Lab Input Test Console
```

Then go to:

```text
Input Builder
```

Use the default topic or enter your own topic and click:

```text
Save JSON package
```
