import abc

class Emailer(abc.ABC):
    def __init__(self, from_address: str, from_name: str):
        self._from_address = from_address
        self._from_name    = from_name

    @abc.abstractmethod
    def send(self, subject,  to_email: str, text_content: str, html_content: str, to_name: str = "user") -> None:
        pass
