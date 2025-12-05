class Message:
    dst_address: str
    dst_port: int

    def __init__(self):
        self.dst_address = None
        self.dst_port = None

    def to_dict(self):
        return {}