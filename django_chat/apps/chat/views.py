from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone

from account.models import UserAccount, Relationship
from .models import PrivateChat, ChatMessage

import json

# Create your views here.
def index(request):
	if not request.user.is_authenticated:
		return redirect('root_index')

	if not request.user.is_verified:
		return redirect('account:verify_email')
		
	return render(request, "chat/index.html")

@csrf_exempt
def search_user(request):
	if (request.method != "POST"):
		return redirect('chat:index')

	if not (request.user.is_authenticated):
		return redirect('root_index')

	if not (request.user.is_verified):
		if not (request.user.is_verifiable()):
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')
	
	response_data = {
		"result" : "",
		"users" : []
	}
	__username = request.POST.get("username", None)

	if not __username:
		response_data["result"] = "FAIL"
		return HttpResponse(json.dumps(response_data))

	users = UserAccount.objects.filter(~Q(username = request.user.username), username__startswith = __username)

	if not users:
		response_data["result"] = "FAIL"
		return HttpResponse(json.dumps(response_data))

	response_data["result"] = "OK"
	for user in users:
		user_data = {
			"username" : user.username,
			"userimage" : user.user_image.url,
			"userid" : user.id,
			"is_friend" : False,
			"has_chat" : False
		}

		rel = Relationship.get_relationship(request.user, user)
		print(rel)

		if rel:
			if rel.rel != "block":
				user_data["has_chat"] = True

				if rel.rel == "friend":
					user_data["is_friend"] = True

		response_data["users"].append(user_data)

	return HttpResponse(json.dumps(response_data))

@csrf_exempt
def get_messages(request):
	if (request.method != "POST"):
		return redirect('chat:index')

	if not (request.user.is_authenticated):
		return redirect('root_index')

	if not (request.user.is_verified):
		if not (request.user.is_verifiable()):
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')

	response_data = {
		"result" : "",
		"messages" : [],
		"first_created" : False
	}

	chat_id = None

	user_id = request.POST.get("userid", None)
	chat_id = request.POST.get("chat_id", None)

	privatechat = None
	if user_id:
		try:
			user = UserAccount.objects.get(id = user_id)
		except:
			response_data["result"] = "FAIL"
			return HttpResponse(json.dumps(response_data))

		if not user:
			response_data["result"] = "FAIL"
			return HttpResponse(json.dumps(response_data))

		rels = Relationship.get_relationship(request.user, user)
		if not rels:
			rels = Relationship.objects.create()
			rels.useraccount_set.add(request.user)
			rels.useraccount_set.add(user)

			privatechat = PrivateChat.objects.create(last_active = timezone.now(), relationship_id = rels.id)
			response_data["first_created"] = True
		else:
			privatechat = rels.privatechat
	elif chat_id:
		try:
			privatechat = PrivateChat.objects.get(id = chat_id)
		except:
			response_data["result"] = "FAIL"
			return HttpResponse(json.dumps(response_data))
	else:
		response_data["result"] = "FAIL"
		return HttpResponse(json.dumps(response_data))

	msgs = []
	try:
		msgs = privatechat.chatmessage_set.order_by("-sent_date")
	except:
		pass

	for msg in msgs:
		msg_data = {
			"sent_date" : msg.sent_date,
			"text" : msg.text,
			"sender" : msg.sender.id
		}

		response_data["messages"].append(msg_data)

	return HttpResponse(json.dumps(response_data))

def get_chats(request):
	if not (request.user.is_authenticated):
		return redirect('root_index')

	if not (request.user.is_verified):
		if not (request.user.is_verifiable()):
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')

	response_data = {
		"result" : "",
		"chats" : []
	}

	rels = request.user.relationships.all()

	for rel in rels:
		if rel.rel == "block":
			continue

		user = rel.get_other_user(request.user.username)
		last_message = rel.privatechat.get_last_message()
		last_message_text = ""

		if last_message:
			last_message_text = last_message.text

		user_data = {
			"username" : user.username,
			"userimage" : user.user_image.url,
			"is_friend" : rel.rel == "friend",
			"chat_id" : rel.privatechat.id,
			"last_message" : last_message_text
		}

		response_data["chats"].append(user_data)

	if response_data["chats"]:
		response_data["result"] = "OK"
	else:
		response_data["result"] = "FAIL"

	return HttpResponse(json.dumps(response_data))

