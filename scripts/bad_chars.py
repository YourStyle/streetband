import re


def check_chars(string: str):
    result = re.match(r"/&#\d{1,6};/gm", f"{str}")
    print(result)
    return result