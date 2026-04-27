# Naz Lab All-in-One Colab Launcher

Use this launcher when you want one cell that can start any Naz Lab workstation.

## Cell 1 - Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2 - Choose and Start Workstation

Change `WORKSTATION="dashboard"` to any supported value:

- `text`
- `dashboard`
- `image`
- `voice`
- `video`
- `portrait`
- `project`

```bash
%%bash
set -Eeuo pipefail

WORKSTATION="dashboard"

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"

if [ ! -d /content/drive/MyDrive ]; then
  echo "ERROR: Google Drive is not mounted. Run Cell 1 first."
  exit 1
fi

case "$WORKSTATION" in
  text)
    APP_REL="text_workstation/app.py"
    REQ_REL="text_workstation/requirements.txt"
    PORT="8501"
    NAME="TEXT WORKSTATION"
    ;;
  dashboard)
    APP_REL="master_dashboard/app.py"
    REQ_REL=""
    PORT="8502"
    NAME="MASTER DASHBOARD"
    ;;
  image)
    APP_REL="image_workstation/app.py"
    REQ_REL="image_workstation/requirements.txt"
    PORT="8503"
    NAME="IMAGE WORKSTATION"
    ;;
  voice)
    APP_REL="voice_workstation/app.py"
    REQ_REL="voice_workstation/requirements.txt"
    PORT="8504"
    NAME="VOICE WORKSTATION"
    ;;
  video)
    APP_REL="video_workstation/app.py"
    REQ_REL="video_workstation/requirements.txt"
    PORT="8505"
    NAME="VIDEO WORKSTATION"
    ;;
  portrait)
    APP_REL="portrait_workstation/app.py"
    REQ_REL="portrait_workstation/requirements.txt"
    PORT="8506"
    NAME="PORTRAIT WORKSTATION"
    ;;
  project)
    APP_REL="project_workstation/app.py"
    REQ_REL="project_workstation/requirements.txt"
    PORT="8507"
    NAME="PROJECT WORKFLOW WORKSTATION"
    ;;
  *)
    echo "ERROR: Unknown WORKSTATION value: $WORKSTATION"
    echo "Use one of: text, dashboard, image, voice, video, portrait, project"
    exit 1
    ;;
esac

APP_PATH="$REPO_DIR/$APP_REL"
STREAMLIT_LOG="/content/streamlit_${WORKSTATION}.log"
CLOUDFLARE_LOG="/content/cloudflared_${WORKSTATION}.log"

echo "=== Naz Lab All-in-One Launcher ==="
echo "Selected: $NAME"
echo "Port: $PORT"
echo "App: $APP_REL"

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

echo ""
echo "=== Latest commit ==="
git log -1 --oneline

echo ""
echo "=== Run Phase 0 validation ==="
python "$REPO_DIR/master_setup/init_drive_structure.py"

echo ""
echo "=== Install dependencies ==="
python -m pip install -q streamlit
if [ -n "$REQ_REL" ] && [ -f "$REPO_DIR/$REQ_REL" ]; then
  python -m pip install -q -r "$REPO_DIR/$REQ_REL"
fi
python -m streamlit --version

echo ""
echo "=== Validate app ==="
python -m py_compile "$APP_PATH"

echo ""
echo "=== Stop old Streamlit/Cloudflare processes ==="
pkill -f streamlit || true
pkill -f cloudflared || true
sleep 2

echo ""
echo "=== Start $NAME ==="
nohup python -m streamlit run "$APP_PATH" \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 8
cat "$STREAMLIT_LOG" | tail -80
curl -I "http://localhost:$PORT" || true

echo ""
echo "=== Start Cloudflare Tunnel ==="
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

nohup /content/cloudflared tunnel --url "http://localhost:$PORT" > "$CLOUDFLARE_LOG" 2>&1 &
sleep 20

PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)

echo ""
echo "=== Cloudflare log ==="
cat "$CLOUDFLARE_LOG" | tail -100

echo ""
echo "============================================================"
echo "NAZ LAB $NAME READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo "============================================================"
```

## Notes

- Cloudflare URLs change every runtime/session.
- Use Dashboard Links tab to save the current public URLs.
- `project` starts the Project Workflow Workstation on port 8507.
- For Voice Workstation reference audio manager, keep using the latest launcher/patch flow until it is made permanent in repo.
