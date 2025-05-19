class EmailNotValidError(Exception):
    pass

def validate_email(email):
    return {'email': email}
