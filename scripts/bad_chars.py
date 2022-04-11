import re


def check_chars(string: str):
    result = re.match(r"/&#\d{1,6};/gm", f"{string}")
    print(result)
    return result
