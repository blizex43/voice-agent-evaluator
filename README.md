# Pretty Good AI Voice Bot Challenge

Python harness for testing a healthcare AI receptionist over Twilio. It can validate configuration, run local scripted scenarios, start a webhook listener, or place a real outbound call.

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in your Groq, Twilio, and ngrok credentials.
3. Set `NGROK_BACKUP_ENDPOINT_URL` to the public URL for your ngrok `/voice` endpoint.

## Commands

```bash
python main.py validate
python main.py validate --twilio
python main.py serve
python main.py run
python main.py call
```

Available scenarios:

```text
refill, appointment, insurance, urgent, angry
```

Outputs are written to:

```text
output/transcripts/
output/reports/
output/recordings/
```

The simulation mode is useful for local debugging without placing a live call, while `serve` and `run` are intended for the Twilio webhook flow.
