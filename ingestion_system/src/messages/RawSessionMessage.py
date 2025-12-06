from .Message import Message
from ..RawSession import RawSession


class RawSessionMessage(Message):
    """
    Message containing a raw session
    """

    raw_session: RawSession
    """
    Raw session to be sent
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.raw_session = None

    def to_dict(self) -> dict:
        """
        Converts the message to dict for easier serialization
        :return: dict
        """
        return self.raw_session.to_dict()