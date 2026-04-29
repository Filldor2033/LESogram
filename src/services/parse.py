import re


MENTION_REGEX = re.compile(r"@(\w{1,32})")

def extract_mentions(text: str) -> list[str]:
    return list(set(MENTION_REGEX.findall(text)))