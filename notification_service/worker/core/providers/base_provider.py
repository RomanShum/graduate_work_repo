from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    async def send_notification(self, to_email, subject, body):
        pass
