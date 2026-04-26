# Naz Lab Phase 1 Text Workstation Runbook

This runbook launches the Text Workstation in Google Colab.

Phase 1 includes General Chat, Story Writer, Viral Script Writer, Caption Writer, Prompt Improver, Output Library, Settings, and Prompt Improver to Image Job Queue.

## Cell 1: Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2: Clone repo

```bash
%%bash
cd /content
rm -rf /content/naz-lab
git clone --depth 1 https://github.com/nazmul73/naz-lab.git /content/naz-lab
cd /content/naz-lab
ls -lah
```

## Cell 3: Run Phase 0 setup first

```bash
%%bash
python /content/naz-lab/master_setup/init_drive_structure.py
```

Expected final output:

```text
PHASE 0 PASSED
```

## Cell 4: Install Text Workstation dependencies

```bash
%%bash
python -m pip install -r /content/naz-lab/text_workstation/requirements.txt
```

## Cell 5: Install zstd and curl before Ollama

```bash
%%bash
apt-get update -y
apt-get install -y zstd curl
```

## Cell 6: Install and start Ollama

```bash
%%bash
curl -fsSL https://ollama.com/install.sh | sh
killall ollama || true
nohup /usr/local/bin/ollama serve > /content/ollama.log 2>&1 &
sleep 10
curl http://localhost:11434/api/tags
```

## Cell 7: Pull and test model

```bash
%%bash
/usr/local/bin/ollama pull gemma2:2b
/usr/local/bin/ollama run gemma2:2b "৫ লাইনের একটি আবেগপূর্ণ বাংলা গল্প লিখো।"
```

## Cell 8: Run Streamlit

```bash
%%bash
pkill -f streamlit || true
nohup python -m streamlit run /content/naz-lab/text_workstation/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > /content/streamlit_text_workstation.log 2>&1 &
sleep 8
cat /content/streamlit_text_workstation.log | tail -120
curl -I http://localhost:8501 || true
```

## Cell 9: Cloudflare Tunnel

```bash
%%bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
chmod +x /content/cloudflared
/content/cloudflared tunnel --url http://localhost:8501
```

## What to test first

1. Open the Cloudflare URL.
2. Save the Cloudflare URL in the Settings tab.
3. Test General Chat with a follow-up question.
4. Test Story Writer.
5. Test Viral Script Writer.
6. Test Caption Writer.
7. Test Prompt Improver and confirm that a JSON file appears in:

```text
/content/drive/MyDrive/NazLab/job_queue/image_jobs
```

8. Check Output Library.

## Notes

- Cloudflare Tunnel is primary.
- Localtunnel is fallback only and is not used in this runbook.
- Do not run the old root-level `app.py` for Phase 1.
- Always run `/content/naz-lab/text_workstation/app.py`.
