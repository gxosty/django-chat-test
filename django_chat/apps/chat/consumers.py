import json
from channels.generic.websocket import AsyncWebsocketConsumer
from account.models import UserAccount
from chat.models import PrivateChat, ChatMessage
from django.utils import timezone

from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
	rooms = []

	async def connect(self):
		await self.accept()

	async def disconnect(self, close_code):
		print("Websocket close_code:", close_code)
		for room_name in self.rooms:
			await self.channel_layer.group_discard(
				room_name,
				self.channel_name
			)
		self.rooms.clear()

	async def receive(self, text_data):
		json_data = json.loads(text_data)
		method = json_data.get("method", None)
		print(text_data)

		if method == "add_chat_room":
			room_name = json_data.get("chat_id", None)
			if room_name != None:
				room_name = "chat_" + str(room_name)
				if room_name not in self.rooms:
					print("Adding room:", room_name)
					self.rooms.append(room_name)
					await self.channel_layer.group_add(
						room_name,
						self.channel_name
					)
		elif method == "remove_chat_room":
			room_name = json_data.get("chat_id", None)
			if room_name != None:
				room_name = "chat_" + str(room_name)
				if room_name in self.rooms:
					self.rooms.remove(room_name)
					await self.channel_layer.group_discard(
						room_name,
						self.channel_name
					)

		elif method == "send_message":
			# example: ChatMessage.objects.create(sent_date = timezone.now(), chat_id = p.id, sender_id = gxost.id, text = "Alright!")

			room_name = json_data.get("chat_id", None)

			if room_name != None:
				room_name = "chat_" + str(room_name)
			else:
				return

			if room_name not in self.rooms:
				return

			__sent_date = timezone.now()

			current_user = await sync_to_async(UserAccount.objects.get, thread_sensitive = True)(id = json_data["sender_id"])
			current_chat = await sync_to_async(PrivateChat.objects.get, thread_sensitive = True)(id = json_data["chat_id"])
			new_message  = await sync_to_async(ChatMessage.objects.create, thread_sensitive = True)(sent_date = __sent_date, chat_id = current_chat.id, sender_id = current_user.id, text = json_data["text"])
			await sync_to_async(new_message.save, thread_sensitive = True)()

			await self.channel_layer.group_send(
				room_name,
				{
					"type" : "send_message",
					"sender_id" : current_user.id,
					"chat_id" : current_chat.id,
					"sent_date" : __sent_date.timestamp(),
					"text" : new_message.text
				}
			)

	async def send_message(self, json_data):
		print("send_message:", json_data)
		json_data["type"] = "add_chat_message"
		await self.send(text_data = json.dumps(json_data))