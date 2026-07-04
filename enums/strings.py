# Centralized string constants for the voice-agent-evaluator.
# Any literal that appears in main bot/ files (file prefixes, webhooks,
# Twilio defaults, etc.) should live here so a single edit propagates
# project-wide.

# ---------------------------------------------------------------------------
# File-name prefixes and extensions
# ---------------------------------------------------------------------------
FILE_PREFIX_REPORT = "report_"
FILE_PREFIX_TRANSCRIPT = "transcript_"
FILE_PREFIX_RECORDING = "recording_"

FILE_EXT_JSON = "json"
FILE_EXT_MD = "md"
FILE_EXT_MP3 = "mp3"

TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"

# ---------------------------------------------------------------------------
# Webhook paths and FastAPI defaults
# ---------------------------------------------------------------------------
WEBHOOK_VOICE_PATH = "/voice"
WEBHOOK_CALL_STATUS_PATH = "/call-status"
WEBHOOK_RECORDING_STATUS_PATH = "/recording-status"
WEBHOOK_HEALTH_PATH = "/health"

SERVICE_NAME = "pretty-good-ai-voice-bot"
MEDIA_TYPE = "application/xml"
EMPTY_TWIML = "<Response />"

# ---------------------------------------------------------------------------
# Twilio / session defaults
# If DEFAULT_USER_INPUT is none, the agent will first listen instead of speak first
# ---------------------------------------------------------------------------
DEFAULT_CALL_SID = "local-test-call"
DEFAULT_RECORDING_SID = "unknown-recording"
DEFAULT_USER_INPUT = None

SIMULATION_SESSION_PREFIX = "simulation-"

# ---------------------------------------------------------------------------
# Twilio status values
# ---------------------------------------------------------------------------
RECORDING_STATUS_COMPLETED = "completed"

# ---------------------------------------------------------------------------
# Timeouts and intervals
# ---------------------------------------------------------------------------
TWILIO_API_TIMEOUT_SECONDS = 30
POLL_INTERVAL_SECONDS = 2