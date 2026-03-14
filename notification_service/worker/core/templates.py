from abc import ABC, abstractmethod
from core.models import User


class BaseTemplate(ABC):
    title = "Base Template"

    @abstractmethod
    def get_message(self):
        pass


class Message(BaseTemplate):
    def __init__(self):
        self.title = "Новое сообщение"

    def get_message(self):
        return "Сообщение"


class PersonalizedMessage(BaseTemplate):
    def __init__(self, user: User):
        self.user = user

    def get_message(self):
        pass


class WelcomeMessage(PersonalizedMessage):
    def __init__(self, user: User):
        super().__init__(user=user)
        self.title = f"Добро пожаловать, {user.name}!"

    def get_message(self):
        return f"Рады приветствовать вас, {self.user.name}, в нашем сервисе!"

class CreatedRoom(PersonalizedMessage):
    def __init__(self, user: User, additional_data: dict):
        super().__init__(user=user)
        self.title = f"Привет, {user.first_name}!"
        self.additional_data = additional_data

    def get_message(self):
        return f"ID комнаты для подключения: {self.additional_data.get("room_id")}!"


class MappingTemplates:
    mapping_messages = {
        "welcome": WelcomeMessage,
        "new": Message,
        "created_room": CreatedRoom
    }

    @classmethod
    def get_template_personalized(cls, template_name: str, user: User, additional_data: dict = None):
        return cls.mapping_messages[template_name](user=user, additional_data=additional_data)

    @classmethod
    def get_template(cls, template_name: str):
        return cls.mapping_messages[template_name]()
