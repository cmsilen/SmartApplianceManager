class Message:
    """
    Class containing the basic attributes of a message
    """

    dst_address: str
    """
    Destination ip address of the message
    """

    dst_port: int
    """
    Destination port of the message
    """

    def __init__(self):
        """
        Constructor
        """
        self.dst_address = None
        self.dst_port = None

    def to_dict(self) -> dict:
        """
        Converts the message to dict for easier serialization
        :return: dict
        """
        return {}