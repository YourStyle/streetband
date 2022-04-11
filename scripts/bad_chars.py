import re


def check_chars(string: str):
    prog = re.compile("&#\d{1,6};")
    result = prog.match(string)
    if result is not None:
        print("Bad char")
        return False
    else:
        print("OK")
        return True
