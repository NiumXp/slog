import slog

slog.quiet("debbug")

slog.debbug("Hi!")
slog.warning("Debbug?")

slog.unquiet()

slog.debbug("Aaaaaaaaa")


with slog.quiet("debbug"):
    slog.debbug("Hello!")
    slog.info("Hi!")

slog.info("Debbug?")
slog.debbug("Hey.")
