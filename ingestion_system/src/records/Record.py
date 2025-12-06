class Record:
    """
    Contains the minimum attributes that a record must implement
    """

    uuid: int
    """
    Unique identifier of the record
    """

    timestamp: str
    """
    Timestamp in which the record was created
    """

    def __init__(self):
        """
        Constructor
        """
        self.uuid = None
        self.timestamp = None