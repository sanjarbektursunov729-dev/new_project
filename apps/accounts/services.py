import secrets
import string
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


def generate_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_username(first_name: str, last_name: str) -> str:
    base = slugify(f"{first_name}.{last_name}".strip(".")) or "admin"
    username = base
    i = 1
    while User.objects.filter(username=username).exists():
        i += 1
        username = f"{base}{i}"
    return username
