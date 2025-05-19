class Context:
    @classmethod
    def instance(cls):
        return cls()
    def socket(self, *args, **kwargs):
        return Socket()
class Socket:
    def connect(self, *args, **kwargs):
        pass
    def send_json(self, *args, **kwargs):
        pass
    def recv_json(self, *args, **kwargs):
        return {}
