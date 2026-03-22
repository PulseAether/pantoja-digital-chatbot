# Pixel — Pantoja Digital Chatbot

AI-powered chatbot backend for [Pantoja Digital](https://pantojadigital.com), built with FastAPI and NeMo Guardrails.

## Features

- **NeMo Guardrails** — Jailbreak protection, topic control, hallucination checks
- **Claude API** — Powered by Anthropic's Claude Sonnet
- **Session Management** — In-memory conversation history per session
- **Railway Ready** — Configured for one-click Railway deployment

## Services Pixel Knows About

| Service | Category |
|---------|----------|
| **NullShield** | AI Security Testing |
| **Tarvix** | Custom AI Agents |
| **Webwright** | Web Development |
| **Beacon** | SEO Optimization |

## Quick Start

```bash
# Clone
git clone https://github.com/PulseAether/pantoja-digital-chatbot.git
cd pantoja-digital-chatbot

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Anthropic API key

# Run
uvicorn app.main:app --reload
```

## API

### Health Check
```
GET /health
```

### Chat
```
POST /api/chat
Content-Type: application/json

{
  "message": "What services do you offer?",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "Pantoja Digital offers four core services...",
  "session_id": "generated-or-provided-id"
}
```

## Deploy to Railway

1. Push to GitHub
2. Connect repo in Railway dashboard
3. Set `ANTHROPIC_API_KEY` environment variable
4. Deploy — Railway auto-detects the config

## Tech Stack

- **FastAPI** — async Python web framework
- **NeMo Guardrails** — NVIDIA's AI safety framework
- **Claude Sonnet** — Anthropic's LLM
- **Railway** — deployment platform
