from Message import Message
from ..records.ExpertRecord import ExpertRecord


class ExpertRecordMessage(Message):
    expert_record: ExpertRecord

    def __init__(self):
        super().__init__()
        self.expert_record = None

    def to_dict(self) -> dict:
        return self.expert_record.to_dict()