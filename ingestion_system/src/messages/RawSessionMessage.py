from .Message import Message
from ..RawSession import RawSession


class RawSessionMessage(Message):
    raw_session: RawSession

    def __init__(self):
        super().__init__()
        self.raw_session = None

    def to_dict(self) -> dict:
        return self.raw_session.to_dict()