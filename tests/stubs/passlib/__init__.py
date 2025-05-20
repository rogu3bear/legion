class context:
    class CryptContext:
        def hash(self, password):
            return "hash"

        def verify(self, password, hashed):
            return True

CryptContext = context.CryptContext
