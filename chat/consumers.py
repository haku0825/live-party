import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage
from parties.models import Party

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['party_id']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        nickname = getattr(self.user, 'nickname', self.user.username)

        # ✅ 메시지를 DB에 비동기로 저장
        await self.save_message(message)

        # 일반 채팅 메시지 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': nickname,
                'sender_id': self.user.id
            }
        )

    # ✅ DB 저장을 위한 헬퍼 함수
    @database_sync_to_async
    def save_message(self, message):
        try:
            party = Party.objects.get(id=self.room_name)
            ChatMessage.objects.create(
                party=party,
                user=self.user,
                content=message
            )
        except Party.DoesNotExist:
            pass

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'system_message',
            'message': event['message'],
        }))

    async def party_killed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'party_killed'
        }))
    
    async def count_update(self, event):
        await self.send(text_data=json.dumps(event))