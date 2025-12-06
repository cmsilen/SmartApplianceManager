from .Message import Message
from ..records.ExpertRecord import ExpertRecord


class ExpertRecordMessage(Message):
    """
    Message containing the label choosen by the expert
    """

    expert_record: ExpertRecord
    """
    Label choosen by the expert to be sent
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.expert_record = None

    def to_dict(self) -> dict:
        """
        Converts the message to dict for easier serialization
        :return:
        """
        return self.expert_record.to_dict()