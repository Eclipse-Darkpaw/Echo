import re

def to_snake_case(string: str) -> str:
    # Replace hyphens and periods with spaces
    string = re.sub(r'[-.]', ' ', string)
    # Insert underscores before uppercase letters and convert to lowercase
    string = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', string).lower()

    return string.replace(' ', '_')