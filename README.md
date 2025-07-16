# 🧠 Twilio AI Voice Assistant with OpenAI Realtime API

This project is a voice-enabled AI assistant built using Twilio Voice and OpenAI's Realtime API. It allows users to call a Twilio number and interact with a smart assistant in real-time using natural language.

---

## 🚀 Overview

- Built with **Python**, **FastAPI**, and **Twilio Programmable Voice**
- Uses **OpenAI GPT-4o Realtime API** to provide real-time responses
- Deployable locally and publicly using **ngrok**
- Logs and handles live speech-to-text and text-to-speech streaming

---

## 📁 Project Structure

```
.
├── main.py                 # FastAPI app logic
├── .env                   # Environment variables (API keys, PORT)
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/adhamali74/twilio-ai-voice-assistant.git
cd twilio-ai-voice-assistant
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the root folder and add:

```env
OPENAI_API_KEY=your_openai_realtime_api_key
PORT=5050
```

### 5. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 5050
```

---

## 🌍 Expose Localhost with ngrok

```bash
ngrok http 5050
```

Use the generated HTTPS URL in your Twilio webhook configuration for the **Voice** webhook.

---

## 🔄 Next Step (Blocked Until Upgrade)

To fully access the OpenAI Realtime API:

- Upgrade to a **paid OpenAI API account**
- Add payment method and purchase credits ($5 minimum)
- Wait for account tier upgrade to unlock realtime model access

---


## 📚 References

- [Twilio Blog Guide](https://www.twilio.com/en-us/blog/voice-ai-assistant-openai-realtime-api-python)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Twilio Voice Docs](https://www.twilio.com/docs/voice)

---

## 📦 Repository

GitHub: [twilio-ai-voice-assistant](https://github.com/adhamali74/twilio-ai-voice-assistant)

---

## 🙋‍♂️ Maintainer

For questions or suggestions, feel free to open an issue or contact [@adhamali74](https://github.com/adhamali74)
