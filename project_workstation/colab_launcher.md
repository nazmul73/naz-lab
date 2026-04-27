# Naz Lab Project Workflow Workstation - Colab Launcher

This launcher starts the Project Workflow Workstation.

## Cell 1 - Mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2 - Start Project Workflow Workstation

```bash
%%bash
set -Eeuo pipefail

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"
APP_PATH="$REPO_DIR/project_workstation/app.py"
STREAMLIT_LOG="/content/streamlit_project_workstation.log"
CLOUDFLARE_LOG="/content/cloudflared_project_workstation.log"

if [ ! -d /content/drive/MyDrive ]; then
  echo "ERROR: Google Drive is not mounted. Run Cell 1 first."
  exit 1
fi

cd /content
if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR"
  git fetch --depth 1 origin main
  git reset --hard origin/main
else
  rm -rf "$REPO_DIR"
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
fi

echo "=== Latest commit ==="
git log -1 --oneline

echo "=== Run Phase 0 validation ==="
python "$REPO_DIR/master_setup/init_drive_structure.py"

echo "=== Install project workstation dependencies ==="
python -m pip install -q -r "$REPO_DIR/project_workstation/requirements.txt"
python -m streamlit --version

echo "=== Validate Project Workstation app ==="
python -m py_compile "$APP_PATH"

echo "=== Start Project Workflow Workstation ==="
pkill -f streamlit || true
pkill -f cloudflared || true
sleep 2
nohup python -m streamlit run "$APP_PATH" \
  --server.port 8507 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 8
cat "$STREAMLIT_LOG" | tail -80
curl -I http://localhost:8507 || true

echo "=== Start Cloudflare Tunnel ==="
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

nohup /content/cloudflared tunnel --url http://localhost:8507 > "$CLOUDFLARE_LOG" 2>&1 &
sleep 20

PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)

echo "=== Cloudflare log ==="
cat "$CLOUDFLARE_LOG" | tail -100

echo ""
echo "============================================================"
echo "NAZ LAB PROJECT WORKFLOW WORKSTATION READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo "============================================================"
```

Expected:

```text
NAZ LAB PROJECT WORKFLOW WORKSTATION READY
Open this URL:
https://something.trycloudflare.com
```
