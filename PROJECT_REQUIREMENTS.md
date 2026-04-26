# Naz Lab AI Workstation - Full Project Requirements

GitHub Repository: https://github.com/nazmul73/naz-lab

## 1. Project Overview

Project name: Naz Lab

Naz Lab is a modular AI workstation built with Google Colab, Streamlit, Ollama, Google Drive, and open-source creative AI tools.

Main workflow:

```text
Idea -> Story -> Script -> Image Prompt -> Image Generation -> Voice Generation -> FaceFusion / LivePortrait -> Final Reel Pack
```

Core principle:

- Do not install all tools in one notebook.
- Keep the main dashboard lightweight.
- Heavy tools must run in separate Colab notebooks/runtimes.
- Save outputs, configs, job plans, and tool links to Google Drive.

## 2. Repository Files

Expected files:

```text
app.py
requirements.txt
README.md
colab_main_dashboard.md
colab_facefusion_lab.md
colab_liveportrait_lab.md
colab_fooocus_image_lab.md
colab_xtts_voice_lab.md
project_plan.md
PROJECT_REQUIREMENTS.md
.gitignore
```

`requirements.txt` must remain Python dependency-only:

```text
streamlit
requests
```

Heavy dependencies must not be added to `requirements.txt`.

## 3. Modular Architecture

### Main Dashboard Notebook

- Streamlit UI
- Ollama backend
- General Chat tab
- AI Agents tab
- Custom Gems tab
- Image Tools tab
- Voice Tools tab
- Video Tools tab
- Output Library
- Settings
- Google Drive output saving
- Job plan saving
- Tool link saving

### FaceFusion Lab

- Separate Colab notebook/runtime
- Install and test now
- Face swap / face enhancement workflow
- Save output to Google Drive

### LivePortrait Lab

- Separate Colab notebook/runtime
- Install and test now
- Static portrait animation using driving video
- Save output to Google Drive

### Fooocus Image Lab

- Separate Colab notebook/runtime
- Planned/later
- Scene-wise image generation
- Save output to Google Drive

### XTTS v2 Voice Lab

- Separate Colab notebook/runtime
- Planned/later
- Text-to-speech / permitted voice generation workflow
- Save output to Google Drive

### Final Reel Pack Lab

- Planned/later
- Package story, script, prompts, images, voice, video notes, captions, and hashtags

## 4. Main Dashboard Requirements

Main dashboard file: `app.py`

Framework: Streamlit

Backend: Ollama

Default model: `gemma2:2b`

Optional model: `mistral`

Ollama generate endpoint:

```text
http://localhost:11434/api/generate
```

Ollama health endpoint:

```text
http://localhost:11434/api/tags
```

Dashboard title:

```text
🧪 Naz Lab AI Workstation
```

Dashboard tabs:

```text
1. Chat
2. AI Agents
3. Custom Gems
4. Image Tools
5. Voice Tools
6. Video Tools
7. Output Library
8. Settings
```

## 5. General Chat Tab

The Chat tab must behave like a normal AI assistant similar to ChatGPT or Gemini.

It must not be limited to one task.

The user should be able to discuss:

- General questions
- Content creation
- Coding
- Google Colab workflow
- GitHub / Codex workflow
- AI tools
- Facebook growth
- Business ideas
- Writing
- Prompt improvement
- Planning
- Productivity
- General knowledge
- Technical discussion
- Project planning
- Scriptwriting
- Marketing
- Automation

Behavior:

- Normal conversational assistant
- Follow-up conversation support
- Chat history during current session
- Use `st.session_state` for messages
- Use `st.chat_message`
- Use `st.chat_input`
- Add Clear Chat button
- Add Save Chat button
- Save chat transcript to `/content/drive/MyDrive/NazLab/outputs`
- Filename format: `naz_lab_chat_YYYY-MM-DD_HH-MM-SS.txt`

General Chat system prompt:

```text
You are Naz Lab General Assistant.
You are a helpful, conversational AI assistant for Nazmul.
You can discuss any topic the user asks about, including content creation, AI tools, coding, Colab workflow, business, productivity, Facebook growth, writing, prompts, and general knowledge.
Answer naturally in the user's language.
If the user writes Bangla, reply in Bangla.
If the user writes English, reply in English.
Do not restrict yourself to one content task.
Ask clarifying questions only when needed.
When the user's prompt is weak, vague, or missing important details, teach the user how to improve the prompt and provide a better prompt version.
```

Prompt rule:

If the user's prompt is weak, incomplete, or unclear, the assistant should teach the user how to write a better prompt and optionally provide an improved prompt version.

## 6. AI Agents Tab

Purpose: one-shot generation mode for specific content tasks.

Default Naz Gems:

### 📖 Storyteller

Purpose: আবেগপূর্ণ গল্প লেখার জন্য।

System prompt:

```text
You are Naz Lab Storyteller.
Write emotional, cinematic, human-like Bangla stories.
Use simple Bangla.
Use short paragraphs.
Avoid robotic language.
```

### 📱 Viral Scripter

Purpose: Facebook Reel / YouTube Shorts script লেখার জন্য।

System prompt:

```text
You are Naz Lab Viral Scripter.
Create short-form video scripts in simple Bangla.
Always include:
1. Title
2. Hook
3. Voiceover
4. On-screen text
5. Caption
6. CTA
```

### 🎬 Video Planner

Purpose: Story থেকে scene-wise video plan বানানোর জন্য।

System prompt:

```text
You are Naz Lab Video Planner.
Create scene-wise video plans for short-form reels.
Always include:
Scene number, visual, camera movement, lighting, mood, image prompt, video prompt, voiceover line.
```

### 💼 Business Guru

Purpose: Marketing, ad copy, customer reply-এর জন্য।

System prompt:

```text
You are Naz Lab Business Guru.
Write practical marketing copy, ad copy, customer replies, and business strategy.
Be clear, direct, and useful.
Avoid fake income claims.
```

AI Agents features:

- User prompt text area
- Generate button
- Output display
- Download output button
- Save output to Google Drive
- Use selected model
- Use selected creativity/temperature
- Use selected Naz Gem system prompt

Output save path:

```text
/content/drive/MyDrive/NazLab/outputs
```

Output filename:

```text
naz_lab_YYYY-MM-DD_HH-MM-SS.txt
```

## 7. Custom Gems Tab

Purpose: create new specialist agents without editing code.

Custom Gems path:

```text
/content/drive/MyDrive/NazLab/config/custom_gems.json
```

Features:

- Create custom gem
- Save custom gem
- Load custom gems into Naz Gem dropdown
- Delete custom gems
- Do not delete default gems
- Handle missing/corrupted JSON safely

Form fields:

```text
1. Gem name
2. Emoji/icon
3. Description
4. System prompt
5. Category
6. Output format notes
```

Saved object should include:

```text
id
name
emoji
display_name
description
system_prompt
category
output_format_notes
created_at
```

Example custom gems:

- 🕵️ True Crime Writer
- 🖼️ Image Prompt Engineer
- 🎙️ Voiceover Script Doctor
- 🧩 Final Reel Pack Builder
- 🧠 Prompt Engineer
- 🧾 Caption Writer
- 🛠️ Colab Helper

## 8. Image Tools Tab

Tool: Fooocus

Purpose: story scene image generation.

Status: separate Image Lab notebook/runtime, planned/later actual installation.

Dashboard should include:

- Fooocus card
- Purpose explanation
- Output folder
- Public link save field
- Image job plan save button

Output folder:

```text
/content/drive/MyDrive/NazLab/image_outputs
```

Image job folder:

```text
/content/drive/MyDrive/NazLab/image_jobs
```

Important:

- Do not install Fooocus inside `app.py`.
- Actual setup stays in `colab_fooocus_image_lab.md`.

## 9. Voice Tools Tab

Tool: XTTS v2

Purpose: text-to-speech / permitted voice generation workflow.

Status: separate Voice Lab notebook/runtime, planned/later actual installation.

Dashboard should include:

- XTTS v2 card
- Purpose explanation
- Reference voice path field
- Script/text field
- Output folder
- Public link save field
- Voice job plan save button
- Safety notice

Output folder:

```text
/content/drive/MyDrive/NazLab/voice_outputs
```

Voice job folder:

```text
/content/drive/MyDrive/NazLab/voice_jobs
```

Safety notice:

Use only your own voice, licensed voice assets, or voices with clear permission. Do not imitate, impersonate, or mislead people.

Important:

- Do not install XTTS v2 inside `app.py`.
- Actual setup stays in `colab_xtts_voice_lab.md`.

## 10. Video Tools Tab

Tools:

```text
1. FaceFusion
2. LivePortrait
```

These two tools should be installable/testable now, but in separate Colab notebooks/runtimes.

Dashboard should include:

- FaceFusion card
- LivePortrait card
- Public link save field
- Job plan save button
- Output folders
- Safety notice

FaceFusion:

- Purpose: face swap / face enhancement / face-related video workflow
- Status: separate FaceFusion Lab install/test now
- Output folder: `/content/drive/MyDrive/NazLab/facefusion_outputs`

LivePortrait:

- Purpose: animate a static portrait image using a driving video or motion reference
- Status: separate LivePortrait Lab install/test now
- Output folder: `/content/drive/MyDrive/NazLab/liveportrait_outputs`

Video job folder:

```text
/content/drive/MyDrive/NazLab/video_jobs
```

Safety notice:

Use only your own face, licensed assets, or people who gave clear permission. Do not impersonate real people. Do not create misleading content.

Important:

- Do not install FaceFusion or LivePortrait inside `app.py`.
- Actual setup stays in `colab_facefusion_lab.md` and `colab_liveportrait_lab.md`.

## 11. Output Library Tab

Purpose: preview saved outputs.

Features:

- Read latest 10 `.txt` files from `/content/drive/MyDrive/NazLab/outputs`
- Select output file
- Preview selected output
- Show file path
- Handle empty folder gracefully

## 12. Settings Tab

Show:

- Ollama endpoint
- Ollama health endpoint
- Base directory
- Output directory
- Config directory
- Custom gems path
- Tool links path
- Text jobs path
- Image jobs path
- Voice jobs path
- Video jobs path
- Image outputs path
- Voice outputs path
- FaceFusion outputs path
- LivePortrait outputs path
- Current model

Button:

```text
Check Ollama Health
```

Health endpoint:

```text
http://localhost:11434/api/tags
```

## 13. Google Drive Folder Structure

```text
/content/drive/MyDrive/NazLab/
├── outputs/
├── config/
│   ├── custom_gems.json
│   └── tool_links.json
├── text_jobs/
├── image_jobs/
├── voice_jobs/
├── video_jobs/
├── image_outputs/
├── voice_outputs/
├── facefusion_outputs/
└── liveportrait_outputs/
```

## 14. Google Colab Setup Instruction

Use active Colab cells, not exported commented code.

Correct active bash cell:

```bash
%%bash
cd /content
git clone --depth 1 https://github.com/nazmul73/naz-lab.git /content/naz-lab
```

Wrong exported code:

```python
# %%bash
# git clone ...
```

When a Colab notebook is exported as `.py`, Colab comments out IPython magic commands like `%%bash`. Those commented commands will not run. The user must paste active cells into Colab.

Main Colab setup sequence:

```text
1. Open new Google Colab notebook
2. Use Chrome browser if possible
3. Runtime -> Change runtime type -> T4 GPU
4. Mount Google Drive
5. Clone GitHub repo using shallow clone
6. Create Drive folders
7. Install Streamlit and requests
8. Copy app.py to /content/app.py
9. Validate app.py
10. Install zstd before Ollama if required
11. Install Ollama
12. Start Ollama server
13. Use /usr/local/bin/ollama if ollama command is not found
14. Pull gemma2:2b
15. Test Ollama
16. Run Streamlit
17. Check localhost:8501
18. Use Cloudflare tunnel, not Localtunnel
19. Open dashboard link
20. Test Chat tab
21. Test AI Agents tab
22. Save output
23. Save job plan
```

## 15. Essential Colab Commands

Mount Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Clone latest repo:

```bash
%%bash
cd /content
rm -rf /content/naz-lab
git clone --depth 1 https://github.com/nazmul73/naz-lab.git /content/naz-lab
cd /content/naz-lab
ls -lah
```

Create Drive folders:

```bash
%%bash
mkdir -p /content/drive/MyDrive/NazLab/outputs
mkdir -p /content/drive/MyDrive/NazLab/config
mkdir -p /content/drive/MyDrive/NazLab/text_jobs
mkdir -p /content/drive/MyDrive/NazLab/image_jobs
mkdir -p /content/drive/MyDrive/NazLab/voice_jobs
mkdir -p /content/drive/MyDrive/NazLab/video_jobs
mkdir -p /content/drive/MyDrive/NazLab/image_outputs
mkdir -p /content/drive/MyDrive/NazLab/voice_outputs
mkdir -p /content/drive/MyDrive/NazLab/facefusion_outputs
mkdir -p /content/drive/MyDrive/NazLab/liveportrait_outputs
```

Install dependencies and copy app:

```bash
%%bash
cd /content/naz-lab
python -m pip install -q streamlit requests
cp /content/naz-lab/app.py /content/app.py
python -m py_compile /content/app.py
grep -n "General Chat" /content/app.py
grep -n "FaceFusion" /content/app.py
```

Install zstd:

```bash
%%bash
apt-get update -y
apt-get install -y zstd curl
zstd --version
```

Install/start Ollama:

```bash
%%bash
curl -fsSL https://ollama.com/install.sh | sh
killall ollama || true
nohup /usr/local/bin/ollama serve > /content/ollama.log 2>&1 &
sleep 10
curl http://localhost:11434/api/tags
```

Pull/test model:

```bash
%%bash
/usr/local/bin/ollama pull gemma2:2b
/usr/local/bin/ollama run gemma2:2b "৫ লাইনের একটি আবেগপূর্ণ বাংলা গল্প লিখো।"
```

Run Streamlit:

```bash
%%bash
pkill -f streamlit || true
nohup python -m streamlit run /content/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --server.enableXsrfProtection false \
  > /content/streamlit.log 2>&1 &
sleep 8
cat /content/streamlit.log | tail -120
curl -I http://localhost:8501 || true
```

Cloudflare tunnel:

```bash
%%bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /content/cloudflared
chmod +x /content/cloudflared
/content/cloudflared tunnel --url http://localhost:8501
```

## 16. Separate Lab Instruction Summary

FaceFusion Lab:

- Separate Colab notebook
- Install/test now
- Save outputs to `facefusion_outputs`
- Save public link/job plan in Video Tools tab

LivePortrait Lab:

- Separate Colab notebook
- Install/test now
- Save outputs to `liveportrait_outputs`
- Save public link/job plan in Video Tools tab

Fooocus Image Lab:

- Separate Colab notebook
- Planned/later
- Save outputs to `image_outputs`
- Save public link/job plan in Image Tools tab

XTTS v2 Voice Lab:

- Separate Colab notebook
- Planned/later
- Save outputs to `voice_outputs`
- Save public link/job plan in Voice Tools tab

## 17. Prompting Guide

Good prompt structure:

```text
Task:
Topic:
Audience:
Language:
Tone:
Output format:
Restrictions:
```

Example:

```text
Task: Facebook Reel script লিখো
Topic: বন্ধুর বিশ্বাসঘাতকতা
Audience: Bangladeshi Facebook audience
Language: সহজ বাংলা
Tone: emotional, cinematic, suspenseful
Output format: title, hook, voiceover, on-screen text, caption, CTA
Restrictions: no gore, no explicit violence, end with a question
```

If the user prompt is weak, Naz Lab General Chat should teach the user how to improve the prompt.

## 18. Roadmap

```text
Phase 1: Main Dashboard + General Chat + Ollama + Gemma
Phase 2: AI Agents + Custom Gems
Phase 3: FaceFusion Lab actual install/test
Phase 4: LivePortrait Lab actual install/test
Phase 5: Fooocus Image Lab
Phase 6: XTTS v2 Voice Lab
Phase 7: Final Reel Pack Generator
Phase 8: Full workflow orchestration
```
