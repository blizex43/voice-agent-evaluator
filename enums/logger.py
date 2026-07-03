import logging

# 1. Instantiate a modular logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the baseline threshold for the logger

# 2. Construct specific destination handlers
console_handler = logging.StreamHandler()   # Sends log data to stderr/stdout
file_handler = logging.FileHandler("errors.log")  # Sends log data to a local file

# 3. Apply operational thresholds to individual handlers
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.ERROR)

# 4. Define and attach a uniform string layout
formatter = logging.Formatter("%(name)s - %(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 5. Bind your configured handlers to your active logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Execution Demonstrations
# logger.info("This text displays on the console, but is excluded from the file.")
# logger.error("This serious error is written to both the file and console outputs.")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
# These wrappers exist so call sites stay readable and consistent.
# Use `log_and_raise(exc, message)` at any risky site (file I/O, network,
# LLM/agent reply) to log the failure with full context and re-raise the
# original exception so the caller can decide what to do.
# ---------------------------------------------------------------------------


def log_info(message: str) -> None:
    """Log an informational message."""
    logger.info(message)


def log_warning(message: str) -> None:
    """Log a warning message."""
    logger.warning(message)


def log_error(message: str) -> None:
    """Log an error message."""
    logger.error(message)


def log_and_raise(exc: BaseException, message: str | None = None) -> None:
    """Log an error (with optional context) and re-raise the given exception.

    The original exception is re-raised unchanged so callers can catch it
    and the original traceback is preserved.
    """
    if message:
        logger.error(f"{message}: {exc}")
    else:
        logger.error(str(exc))
    raise exc
