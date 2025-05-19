class Client:
    def __init__(self, *args, **kwargs):
        pass
    def request(self, *args, **kwargs):
        class Response:
            status_code = 200
            def json(self):
                return {}
        return Response()
