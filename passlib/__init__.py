class context:
    class CryptContext:
        def __init__(self, *args, **kwargs):
            pass

        def hash(self, password):
            return "hash"

        def verify(self, password, hashed):
            return True


CryptContext = context.CryptContext
