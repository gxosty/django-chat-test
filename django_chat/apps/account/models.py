from django.conf import settings
from django.db import models

from django.utils import timezone
import datetime
from django.contrib.auth.models import AbstractUser, User
from django.db.models import Q

from uuid import uuid4
import os

from PIL import Image

class UserAccount(AbstractUser):
	def image_uploaded(instance, filename):
		ext = os.path.splitext(filename)
		if (len(ext) > 1):
			ext = ext[1]
		else:
			ext = ""

		return os.path.join("images", "user_images", str(instance.id) + "_" + str(uuid4()).replace("-", "") + ext)

	user_image  = models.ImageField(upload_to = image_uploaded, default = settings.USER_NO_PFP)
	dark_theme  = models.BooleanField(default = False)
	
	is_verified = models.BooleanField("Email Verified", default = False)
	verification_sent_date = models.DateTimeField(null = True)
	email_code  = models.CharField("Email Code", max_length = 5, default = "xxxxx")

	relationships = models.ManyToManyField('Relationship')

	def is_usable(self):
		if not self.is_verified:
			return False

		if not self.is_active:
			return False

		return True

	def is_verifiable(self):
		return (self.verification_sent_date > (timezone.now() - datetime.timedelta(hours = settings.EMAIL_VERIFICATION_EXPIRE))) or self.is_verified

	def save(self, **kwargs):
		super().save(**kwargs)

		# If user have a profile picture, crop it
		if (self.user_image.path.find(settings.USER_NO_PFP) == -1):
			with Image.open(self.user_image.path) as image:
				width, height = image.size

				# only process if size is not 28x28
				if (width != 28 or height != 28):
					# if picture is not square, crop it centered
					if (width != height):
						if (width > height):
							offset = (width - height) // 2
							image = image.crop((
								offset,         0,
								width - offset, height
							))
						else:
							offset = (height - width) // 2
							image = image.crop((
								0,     offset,
								width, height - offset
							))

					image = image.resize(
						(28, 28)
					)

					image.save(self.user_image.path)


class Relationship(models.Model):
	RELATIONSHIP_STATE = (
		("friend", "Friend"),
		("mate", "Mate"),
		("block", "Block")
	)

	rel = models.CharField(
		max_length = 6,
		choices = RELATIONSHIP_STATE,
		default = "mate"
	)

	# Returns relationship between two users
	def get_relationship(__user1, __user2):
		rel1 = __user1.relationships.all()

		for _rel in rel1:
			_rel2 = __user2.relationships.filter(id = _rel.id)
			if _rel2:
				return _rel2[0]

		return None

	def get_other_user(self, __username):
		users = self.useraccount_set.filter(~Q(username = __username))

		if users:
			return users[0]
		return None