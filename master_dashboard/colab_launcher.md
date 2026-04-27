# Naz Lab Master Control Dashboard - Colab Launcher

This launcher starts only the Master Control Dashboard. Run it after Google Drive is mounted.

## Cell 1 - Mount Drive

### এই cell কী করবে

Google Drive mount করবে, যাতে Dashboard Naz Lab folders, logs, configs, outputs, and job queue read করতে পারে।

### আপনার করণীয়

Colab-এ normal Python cell হিসেবে run করুন।

### Exact code

```python
from google.colab import drive
drive.mount('/content/drive')
```

### Expected result

```text
Mounted at /content/drive
```

### Error হলে কী করবেন

Runtime disconnect করে আবার mount করুন। Drive mount না হলে Dashboard চালাবেন না।

---

## Cell 2 - Start Master Dashboard

### এই cell কী করবে

1. GitHub repo clone/update করবে।
2. Phase 0 Drive structure validate করবে।
3. Dashboard dependencies install করবে।
4. Master Dashboard Streamlit app start করবে।
5. Cloudflare Tunnel URL print করবে।

### আপনার করণীয়

Colab-এ `%%bash` cell হিসেবে run করুন।

### Exact code

```bash
%%bash
set -Eeuo pipefail

REPO_URL="https://github.com/nazmul73/naz-lab.git"
REPO_DIR="/content/naz-lab"
APP_PATH="$REPO_DIR/master_dashboard/app.py"
STREAMLIT_LOG="/content/streamlit_master_dashboard.log"
CLOUDFLARE_LOG="/content/cloudflared_master_dashboard.log"

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

echo "=== Install dashboard dependencies ==="
python -m pip install -q -r "$REPO_DIR/master_dashboard/requirements.txt"
python -m streamlit --version

echo "=== Validate dashboard app ==="
python -m py_compile "$APP_PATH"

echo "=== Start Master Dashboard ==="
pkill -f streamlit || true
sleep 2
nohup python -m streamlit run "$APP_PATH" \
  --server.port 8502 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > "$STREAMLIT_LOG" 2>&1 &

sleep 8
cat "$STREAMLIT_LOG" | tail -80
curl -I http://localhost:8502 || true

echo "=== Start Cloudflare Tunnel ==="
if [ ! -x /content/cloudflared ]; then
  wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
  chmod +x /content/cloudflared
fi

pkill -f cloudflared || true
sleep 2
nohup /content/cloudflared tunnel --url http://localhost:8502 > "$CLOUDFLARE_LOG" 2>&1 &
sleep 15

PUBLIC_URL=$(grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' "$CLOUDFLARE_LOG" | head -1 || true)

echo "=== Cloudflare log ==="
cat "$CLOUDFLARE_LOG" | tail -80

echo ""
echo "============================================================"
echo "NAZ LAB MASTER DASHBOARD READY"
echo "Open this URL:"
echo "$PUBLIC_URL"
echo "============================================================"
```

### Expected result

```text
NAZ LAB MASTER DASHBOARD READY
Open this URL:
https://something.trycloudflare.com
```

### Error হলে কী করবেন

If no URL appears, run:

```bash
%%bash
cat /content/cloudflared_master_dashboard.log | tail -120
```

If Streamlit does not start, run:

```bash
%%bash
cat /content/streamlit_master_dashboard.log | tail -120
```

---

## Dashboard tabs

- Status
- Workstations
- Outputs
- Job Queue
- Roadmap

## Product requirement

Bangla and English output quality are primary requirements. Other languages are optional.
