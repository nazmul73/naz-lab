# Naz Lab Main Dashboard Colab Runbook

Run these cells in order in a clean Google Colab notebook.

## Cell 1: Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## Cell 2: Set paths

```python
REPO_URL = "https://github.com/nazmul73/naz-lab.git"
PROJECT_DIR = "/content/naz-lab"
APP_PATH = "/content/app.py"
DRIVE_BASE = "/content/drive/MyDrive/NazLab"
```

## Cell 3: Create folders

```bash
!mkdir -p /content/drive/MyDrive/NazLab/outputs
!mkdir -p /content/drive/MyDrive/NazLab/scripts
!mkdir -p /content/drive/MyDrive/NazLab/prompts
!mkdir -p /content/drive/MyDrive/NazLab/config
!mkdir -p /content/drive/MyDrive/NazLab/text_jobs
!mkdir -p /content/drive/MyDrive/NazLab/image_jobs
!mkdir -p /content/drive/MyDrive/NazLab/voice_jobs
!mkdir -p /content/drive/MyDrive/NazLab/video_jobs
!mkdir -p /content/drive/MyDrive/NazLab/image_outputs
!mkdir -p /content/drive/MyDrive/NazLab/voice_outputs
!mkdir -p /content/drive/MyDrive/NazLab/facefusion_outputs
!mkdir -p /content/drive/MyDrive/NazLab/liveportrait_outputs
```

## Cell 4: Clone or update GitHub repo

```bash
%cd /content

if [ -d "/content/naz-lab/.git" ]; then
  echo "Repo already exists. Pulling latest changes..."
  cd /content/naz-lab && git pull
else
  echo "Cloning repo..."
  git clone https://github.com/nazmul73/naz-lab.git /content/naz-lab
fi

cd /content/naz-lab
ls -la
```

## Cell 5: Verify files

```bash
%cd /content/naz-lab

test -f app.py && echo "OK: app.py" || echo "MISSING: app.py"
test -f requirements.txt && echo "OK: requirements.txt" || echo "MISSING: requirements.txt"
test -f README.md && echo "OK: README.md" || echo "MISSING: README.md"
test -f colab_main_dashboard.md && echo "OK: colab_main_dashboard.md" || echo "MISSING: colab_main_dashboard.md"
test -f colab_facefusion_lab.md && echo "OK: colab_facefusion_lab.md" || echo "MISSING: colab_facefusion_lab.md"
test -f colab_liveportrait_lab.md && echo "OK: colab_liveportrait_lab.md" || echo "MISSING: colab_liveportrait_lab.md"
test -f colab_fooocus_image_lab.md && echo "OK: colab_fooocus_image_lab.md" || echo "MISSING: colab_fooocus_image_lab.md"
test -f colab_xtts_voice_lab.md && echo "OK: colab_xtts_voice_lab.md" || echo "MISSING: colab_xtts_voice_lab.md"
test -f project_plan.md && echo "OK: project_plan.md" || echo "MISSING: project_plan.md"
```

## Cell 6: Install dashboard dependencies

```bash
%cd /content/naz-lab
!pip install -q -r requirements.txt
!npm install -g localtunnel
```

## Cell 7: Copy app.py

```bash
cp /content/naz-lab/app.py /content/app.py
wc -l /content/app.py
head -20 /content/app.py
```

## Cell 8: Validate app.py

```bash
grep -n "Viral" /content/app.py
grep -n "Fooocus" /content/app.py
grep -n "XTTS" /content/app.py
grep -n "FaceFusion" /content/app.py
grep -n "LivePortrait" /content/app.py
python -m py_compile /content/app.py
```

## Cell 9: Install Ollama

```bash
!curl -fsSL https://ollama.com/install.sh | sh
```

## Cell 10: Start Ollama

```bash
!killall ollama || true
!nohup ollama serve > /content/ollama.log 2>&1 &
```

## Cell 11: Wait

```python
import time
time.sleep(10)
```

## Cell 12: Check Ollama

```bash
!curl http://localhost:11434/api/tags
```

## Cell 13: Pull default model

```bash
!ollama pull gemma2:2b
```

## Cell 14: Optional Mistral

```bash
!ollama pull mistral
```

## Cell 15: Test model

```bash
!ollama run gemma2:2b "৫ লাইনের একটি আবেগপূর্ণ বাংলা গল্প লিখো।"
```

## Cell 16: Run Streamlit

```bash
!pkill -f streamlit || true
!streamlit run /content/app.py --server.port 8501 > /content/streamlit.log 2>&1 &
```

## Cell 17: Check logs

```bash
!cat /content/streamlit.log | tail -80
```

## Cell 18: Start public link

```bash
!npx localtunnel --port 8501
```

## Cell 19: Localtunnel password if needed

```bash
!curl ipv4.icanhazip.com
```

## First dashboard test

Select `📱 Viral Scripter` and run:

```text
একটি ৬০ সেকেন্ডের Facebook Reel script লিখো।
Topic: বন্ধুর বিশ্বাসঘাতকতা।
Language: সহজ বাংলা।
Tone: emotional, cinematic, suspenseful.
Include: title, hook, voiceover, on-screen text, caption, CTA.
```
