import json
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message, last_10_message

User = get_user_model()

class ChatConsumer(WebsocketConsumer):

    def fetch_message(self, data):
        # print("Fetch - ",data) # Fetch - {"message": "hey", "command": "fetch_message"}
        messages = last_10_message()
        content = {
            "messages": self.message_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, str_data):
        # print("New - ", type(data))
        data = json.loads(str_data)
        author = data['form']

        author_user = User.objects.filter(username= author)[0]
        # print("author_user - ", author_user)
        message = Message.objects.create(author=author_user, content=data['message'])
        # print("message - ", message)
        content = {
            'command': "new_message",
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.messages_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }



    commands = {
        'fetch_message': fetch_message,
        'new_message': new_message
    }

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.commands[text_data_json['command']](self, text_data)

    def send_chat_message(self, message):
        # message = text_data_json['message']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))


