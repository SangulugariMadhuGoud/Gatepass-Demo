from django.core.exceptions import ValidationError
import re

def validate_password_strength(password):
    """
    Validate that a password meets minimum requirements:
    - Contains at least 5 alphabet characters (letters)
    - Contains at least 5 numbers
    - Contains at least one special character
    """
    # Count alphabet characters (both uppercase and lowercase)
    alphabet_count = len(re.findall(r'[A-Za-z]', password))
    if alphabet_count < 5:
        raise ValidationError("Password must contain at least 5 alphabet characters (letters).")

    # Count numbers
    number_count = len(re.findall(r'\d', password))
    if number_count < 5:
        raise ValidationError("Password must contain at least 5 numbers.")

    # Check for special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?]', password):
        raise ValidationError("Password must contain at least one special character (e.g., !@#$%^&*).")
