import re


def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

def is_strong_password(password):
    
    password_criteria = [
        r'[A-Z]',         
        r'[a-z]',         
        r'[0-9]',         
        r'[!@#$%^&*(),.?":{}|<>]',
    ]

    if len(password) < 8:
        return False
    
    for pattern in password_criteria:
        if not re.search(pattern, password):
            return False

    return True  
  