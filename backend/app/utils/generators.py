"""
Generator utilities - Random strings, codes, etc.
"""

import secrets
import string
import uuid
from typing import Optional


def generate_referral_code(length: int = 8) -> str:
    """
    Generate unique referral code.
    
    Example: "A3B7K9M2"
    """
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_random_string(
    length: int = 32,
    include_lowercase: bool = True,
    include_uppercase: bool = True,
    include_digits: bool = True,
    include_special: bool = False,
) -> str:
    """
    Generate random string with customizable character set.
    
    Args:
        length: Length of string
        include_lowercase: Include a-z
        include_uppercase: Include A-Z
        include_digits: Include 0-9
        include_special: Include !@#$%^&*
    """
    chars = ""
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special:
        chars += "!@#$%^&*"
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_otp(length: int = 6) -> str:
    """
    Generate numeric OTP code.
    
    Example: "847291"
    """
    return "".join(secrets.choice(string.digits) for _ in range(length))


def generate_uuid() -> str:
    """Generate UUID4 string."""
    return str(uuid.uuid4())


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate URL-safe slug from text.
    
    Example: "Hello World!" -> "hello-world"
    """
    import re
    
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    
    # Truncate
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    
    return slug