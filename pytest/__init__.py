def mark(*args, **kwargs):
    def decorator(func):
        return func
    return decorator
