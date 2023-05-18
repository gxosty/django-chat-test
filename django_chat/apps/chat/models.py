from django.db import models
from django.utils import timezone

from account.models import UserAccount, Relationship

# Create your models here.
class PrivateChat(models.Model):
	relationship = models.OneToOneField(Relationship, on_delete = models.CASCADE)
	last_active = models.DateTimeField()

	def get_last_message(self):
		# self.chatmessage_set.last()
		msgs = self.chatmessage_set.order_by("-sent_date")

		if msgs:
			return msgs[0]
			
		return None

class ChatMessage(models.Model):
	chat = models.ForeignKey(PrivateChat, on_delete = models.CASCADE)
	sent_date = models.DateTimeField()
	text = models.TextField()
	sender = models.ForeignKey(UserAccount, on_delete = models.CASCADE)

