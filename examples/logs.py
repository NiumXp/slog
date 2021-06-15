import slog

log = slog.Log()
log.info("Simple!")

# Creates a file log when context manager ends!
with slog.Log() as log:
    log.info("Heyy!")
