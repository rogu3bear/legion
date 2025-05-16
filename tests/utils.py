import random
import string


def random_email() -> str:
    # Basic placeholder
    username = "".join(random.choice(string.ascii_lowercase) for i in range(8))
    domain = "".join(random.choice(string.ascii_lowercase) for i in range(5))
    return f"{username}@{domain}.com"


def random_lower_string(length: int = 10) -> str:
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))
