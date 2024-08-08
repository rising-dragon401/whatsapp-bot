import secrets

def generate_id(length):
    return secrets.token_urlsafe(length)[:length]