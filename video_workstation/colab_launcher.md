# Naz Lab Video Workstation - Colab Launcher

This launcher starts only the Video Workstation. Run it after Google Drive is mounted.

## Cell 1 - Mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2 - Start Video Workstation

```bash
%%bash
set -Eeuo pipefail

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"
APP_PATH="$REPO_DIR/video_workstation/app.py"
STREAMLIT_LOG="/content/streamlit_video_workstation.log"
CLOUDFLARE_LOG="/content/cloudflared_video_workstation.log"

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

echo "=== Install video workstation dependencies ==="
python -m pip install -q -r "$REPO_DIR/video_workstation/requirements.txt"
python -m streamlit --version

echo "=== Validate Video Workstation app ==="
python -m py_compile "$APP_PATH"

echo "=== Start Video Workstation ==="
pkill -f streamlit || true
sleep 2
nohup python -m streamlit run "$APP_PATH" \
  --server.port 8505 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 8
cat "$STREAMLIT_LOG" | tail -80
curl -I http://localhost:8505 || true

echo "=== Start Cloudflare Tunnel ==="
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

pkill -f cloudflared || true
sleep 2
nohup /content/cloudflared tunnel --url http://localhost:8505 > "$CLOUDFLARE_LOG" 2>&1 &
sleep 15

PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)

echo "=== Cloudflare log ==="
cat "$CLOUDFLARE_LOG" | tail -80

echo ""
echo "============================================================"
echo "NAZ LAB VIDEO WORKSTATION READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo "============================================================"
```

Expected result:

```text
NAZ LAB VIDEO WORKSTATION READY
Open this URL:
https://something.trycloudflare.com
```

## Tabs

- Status
- Builder
- Inputs
- Library
- Launch

## Phase 5.0 scope

This foundation version creates video packages and storyboards. It does not generate video yet.
