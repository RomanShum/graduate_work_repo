from core.templates import MappingTemplates
from core.auth import auth_client
from core.models import User
from core.providers.email_provider import EmailProvider


class Sender:
    def __init__(self):
        self.__auth_service = auth_client
        self.provider = EmailProvider()

    async def __prepare_message(self, message, user: User | None = None):
        if user:
            template = MappingTemplates.get_template_personalized(template_name=message.get('type'), user=user)
        else:
            template = MappingTemplates.get_template(template_name=message.get('type'))

        return template

    async def send(self, message):
        user = None
        if message.get('object_id'):
            user = await self.__auth_service.get_user_data(message.get('object_id'))
            if not user:
                raise Exception("User not found")
            user = User.model_validate(user)
        prepared_message = await self.__prepare_message(message, user)
        await self.provider.send_notification(id_message=message.get('id'), to_email=user.email, subject=prepared_message.title,
                                       body=prepared_message.get_message())
        return True
