import slog


def error(message):
    raise Exception(message)


@slog.observe(suppress=True)
def greeting(user: str):
    return error("Hello " + user + '!')


name = input("Name: ")
slog.debbug("User typed '{}'", name)

greeting(name)
