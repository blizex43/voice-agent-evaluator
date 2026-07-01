# Pretty Good AI Voice Bot Challenge

Python voice-bot harness for testing a healthcare AI receptionist over Twilio.

## Setup

1. Copy `.env.example` to `.env`.
2. Fill in Groq and Twilio credentials.
3. Set `ENDPOINT_URL` to your public ngrok `/voice` URL.

## Commands

```bash
python main.py validate
python main.py validate --twilio
python main.py simulate --scenario refill
python main.py serve
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
