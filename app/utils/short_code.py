import random
import string

CHARACTERS = string.ascii_letters + string.digits
CODE_LENGTH = 6


def generate_short_code(length: int = CODE_LENGTH) -> str:
    return "".join(random.choices(CHARACTERS, k=length))
