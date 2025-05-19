class JWTError(Exception):
    pass

def jwt_encode(payload, key, algorithm="HS256"):
    return "token"

def jwt_decode(token, key, algorithms=None):
    return {}

jwt = type("jwt", (), {"encode": jwt_encode, "decode": jwt_decode})
