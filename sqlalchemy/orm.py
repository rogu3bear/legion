class Session:
    pass
class DeclarativeBase:
    pass

def declarative_base(*args, **kwargs):
    class Base:
        pass
    return Base

def relationship(*args, **kwargs):
    pass

def sessionmaker(*args, **kwargs):
    return lambda: None
