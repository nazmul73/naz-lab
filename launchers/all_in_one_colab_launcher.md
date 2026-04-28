# Naz Lab All-in-One Colab Launcher

Use this launcher when you want one cell that can start any Naz Lab workstation and return an openable Cloudflare public URL.

## Cell 1 - Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2 - Choose and Start Workstation

Change `WORKSTATION="test"` to any supported value:

- `test` — Input Test Console, best for frontend testing
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

WORKSTATION="test"

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"
LOCAL_HOST="127.0.0.1"

if [ ! -d /content/drive/MyDrive ]; then
  echo "ERROR: Google Drive is not mounted. Run Cell 1 first."
  exit 1
fi

case "$WORKSTATION" in
  test)
    APP_REL="test_console/app.py"
    REQ_REL=""
    PORT="8508"
    NAME="INPUT TEST CONSOLE"
    ;;
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
    echo "Use one of: test, text, dashboard, image, voice, video, portrait, project"
    exit 1
    ;;
esac

APP_PATH="$REPO_DIR/$APP_REL"
STREAMLIT_LOG="/content/streamlit_${WORKSTATION}.log"
CLOUDFLARE_LOG="/content/cloudflared_${WORKSTATION}.log"

print_section() {
  echo ""
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

print_section "Naz Lab All-in-One Launcher"
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

print_section "Latest commit"
git log -1 --oneline

print_section "Run Phase 0 validation"
python "$REPO_DIR/master_setup/init_drive_structure.py"

print_section "Install dependencies"
python -m pip install -q streamlit
if [ -n "$REQ_REL" ] && [ -f "$REPO_DIR/$REQ_REL" ]; then
  python -m pip install -q -r "$REPO_DIR/$REQ_REL"
fi
python -m streamlit --version

print_section "Validate app"
python -m py_compile "$APP_PATH"

print_section "Stop old Streamlit/Cloudflare processes"
pkill -f streamlit || true
pkill -f cloudflared || true
sleep 2

print_section "Start $NAME"
nohup python -m streamlit run "$APP_PATH" \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 10
cat "$STREAMLIT_LOG" | tail -100

print_section "Check Streamlit health"
if ! pgrep -f "streamlit run .*${APP_REL}" >/dev/null 2>&1; then
  echo "ERROR: Streamlit process is not running. Showing log:"
  cat "$STREAMLIT_LOG"
  exit 1
fi

if ! curl -fsS "http://${LOCAL_HOST}:${PORT}" >/tmp/naz_lab_health_${WORKSTATION}.html 2>/tmp/naz_lab_health_${WORKSTATION}.err; then
  echo "ERROR: Streamlit is running but not responding on http://${LOCAL_HOST}:${PORT}"
  echo "Curl error:"
  cat /tmp/naz_lab_health_${WORKSTATION}.err || true
  echo "Streamlit log:"
  cat "$STREAMLIT_LOG"
  exit 1
fi

echo "Streamlit health check OK: http://${LOCAL_HOST}:${PORT}"

print_section "Start Cloudflare Tunnel"
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

nohup /content/cloudflared tunnel --url "http://${LOCAL_HOST}:${PORT}" > "$CLOUDFLARE_LOG" 2>&1 &

PUBLIC_URL=""
for attempt in $(seq 1 30); do
  PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)
  if [ -n "$PUBLIC_URL" ]; then
    break
  fi
  sleep 2
done

print_section "Cloudflare log"
cat "$CLOUDFLARE_LOG" | tail -120

if [ -z "$PUBLIC_URL" ]; then
  echo "ERROR: Cloudflare public URL was not created."
  echo "Check Streamlit log at: $STREAMLIT_LOG"
  echo "Check Cloudflare log at: $CLOUDFLARE_LOG"
  exit 1
fi

print_section "NAZ LAB $NAME READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo ""
echo "If the link does not open immediately, wait 10-20 seconds and refresh once."
echo "Streamlit log: $STREAMLIT_LOG"
echo "Cloudflare log: $CLOUDFLARE_LOG"
```

## Notes

- Use `WORKSTATION="test"` for the frontend Input Test Console.
- Cloudflare URLs change every runtime/session.
- This launcher uses `127.0.0.1` instead of `localhost` to avoid Colab IPv6 origin issues.
- Use Dashboard Links tab to save the current public URLs.
- `project` starts the Project Workflow Workstation on port 8507.
- If a URL is not printed, the launcher will show a clear error and the relevant log paths.
