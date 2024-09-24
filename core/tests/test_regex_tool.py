import re

line = 'auth\t[default=die]\tpam_faillock.so\tauthfail'
regex = "\\.*ACCEPT\\.*all\\.*lo\\.*.\\.*0.0.0.0/0\\.*0.0.0.0/0"

try:
    re.compile(regex)
    is_valid = True
except re.error as e:
    is_valid = False
    error_message = str(e)

if is_valid:
    match = bool(re.search(regex, line))
    print(f"Regex is valid: {is_valid}. Match result: {match}")
else:
    print(f"Invalid regex: {error_message}")
