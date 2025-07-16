import os
import json
import base64
import asyncio
from websockets.client import connect  # ✅ NEW import for correct client connection
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # ✅ Requires OpenAI Realtime API Access
PORT = int(os.getenv('PORT', 5050))  # ✅ Default port fallback if not set

# Defines the AI’s personality
SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about "
    "anything the user is interested in and is prepared to offer them facts. "
    "You have a penchant for dad jokes, owl jokes, and rickrolling – subtly. "
    "Always stay positive, but work in a joke when appropriate."
)

VOICE = 'alloy'  # ✅ Chosen OpenAI voice

# What you’ll see in logs (OpenAI stream events)
LOG_EVENT_TYPES = [
    'response.content.done', 'rate_limits.updated', 'response.done',
    'input_audio_buffer.committed', 'input_audio_buffer.speech_stopped',
    'input_audio_buffer.speech_started', 'session.created'
]

app = FastAPI()

# Raise error if API key is missing
if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

@app.get("/", response_class=JSONResponse)
async def index_page():
    # For testing the server
    return {"message": "Twilio Media Stream Server is running!"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> to improve text-to-speech flow
    response.say("Please wait while we connect your call to the A. I. voice assistant, powered by Twilio and the Open-A.I. Realtime API")
    response.pause(length=1)
    response.say("O.K. you can start talking!")

    host = request.url.hostname
    connect_elem = Connect()
    connect_elem.stream(url=f'wss://{host}/media-stream')
    response.append(connect_elem)

    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("🟢 Client connected to /media-stream WebSocket")
    await websocket.accept()

    headers = [  # ✅ FIXED: headers must be a list of tuples
        ("Authorization", f"Bearer {OPENAI_API_KEY}"),
        ("OpenAI-Beta", "realtime=v1")
    ]

    async with connect(
    'wss://api.openai.com/v1/realtime?model=gpt-4o',

        extra_headers=headers
    ) as openai_ws:
        await send_session_update(openai_ws)
        print("✅ Session update sent to OpenAI WebSocket")

        stream_sid = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"📶 Incoming stream has started: {stream_sid}")
                    elif data['event'] == 'stop':
                        print("🛑 Stream stopped by Twilio")
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"📨 Received event: {response['type']}", response)
                    if response['type'] == 'session.updated':
                        print("🔄 Session updated successfully:", response)
                    if response['type'] == 'response.audio.delta' and response.get('delta'):
                        try:
                            audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_payload
                                }
                            }
                            await websocket.send_json(audio_delta)
                        except Exception as e:
                            print(f"❌ Error processing audio data: {e}")
            except Exception as e:
                print(f"❌ Error in send_to_twilio: {e}")

        async def keep_alive():
            """Ping OpenAI every 10 seconds to keep the WebSocket alive."""
            try:
                while True:
                    await asyncio.sleep(10)
                    await openai_ws.send(json.dumps({"type": "ping"}))
            except Exception as e:
                print(f"⚠️ Keep-alive failed: {e}")

        await asyncio.gather(receive_from_twilio(), send_to_twilio(), keep_alive())

async def send_session_update(openai_ws):
    """Send session update to OpenAI WebSocket."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},  # To know when you stop speaking
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8  # Controls creativity of responses
        }
    }
    print('📤 Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
