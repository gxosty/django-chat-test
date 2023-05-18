from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.conf import settings

from .models import UserAccount
from .email_funcs import EmailVerificator
from django.contrib.auth.models import auth
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.utils import timezone
import datetime

from string import ascii_uppercase, digits
import random
import math

import colorama as clr
import os

# call :colorama.init: if using windows
if os.name == "nt":
	print("[I] Initializing Colorama")
	clr.init()

EMAIL_VERIFICATOR = EmailVerificator(
	settings.EMAIL_FOR_VERIFICATION,
	settings.EMAIL_FOR_VERIFICATION_PASS
)

EMAIL_VERIFICATION_CHARS = [
	ascii_uppercase,
	digits
]

EMAIL_VERIFICATION_MESSAGE = """Subject: Email Verification Code | Django-Chat

Hello dear %s!
You signed up in Django-Chat using this Email.
Please, provide this 5-character code in Django-Chat in order to successfully verify your account:

%s

Thanks you!

"""

def generate_email_verification_code():
	global EMAIL_VERIFICATION_CHARS

	res = ""

	for i in range(5):
		res += random.choice(random.choice(EMAIL_VERIFICATION_CHARS))

	return res

def send_email_verification_code(user):
	global EMAIL_VERIFICATOR
	global EMAIL_VERIFICATION_MESSAGE

	user.email_code = generate_email_verification_code()

	try:
		EMAIL_VERIFICATOR.send_to(user.email, EMAIL_VERIFICATION_MESSAGE % (user.username, user.email_code))
	except Exception as ex:
		print(clr.FORE.RED + "Email Verification Send Error:", ex, clr.FORE.RESET)

	user.verification_sent_date = timezone.now()
	user.save()

def verify_email_code(user, code):
	if user.email_code == code:
		user.is_verified = True
		user.save()
		return True

	return False

# Create your views here.
def send_verification_code(request):
	if (request.method == "POST"):
		if (request.user.is_authenticated):
			if not (request.user.is_verified):
				if not (request.user.is_verifiable()):
					user = request.user
					auth.logout(request)
					user.delete()
					return redirect('root_index')

				if (request.user.verification_sent_date > (timezone.now() - datetime.timedelta(seconds = 30))):
					messages.info(request, "Wait 30 seconds")
				else:
					messages.info(request, "Verification code was re-sent")
					send_email_verification_code(request.user)

	return redirect('account:verify_email')

def login(request):
	if request.user.is_authenticated:
		if not request.user.is_verified:
			if not (request.user.is_verifiable()):
				user = request.user
				auth.logout(request)
				user.delete()
				return redirect('root_index')

			return redirect('account:verify_email')
		return redirect('root_index')

	if request.method == "POST":
		__username = request.POST["username"]
		__password = request.POST["password"]

		user = auth.authenticate(username = __username, password = __password)

		if user is None:
			messages.info(request, "Invalid username or password")
			return redirect('account:login')
		else:
			auth.login(request, user)
			if not user.is_verified:
				return redirect('account:verify_email')
			return redirect('root_index')

	if request.method == "GET":
		return render(request, 'account/login.html')

def verify_email(request):
	if not request.user.is_authenticated:
		return redirect('root_index')

	if request.user.is_verified:
		return redirect('root_index')
	else:
		if not (request.user.is_verifiable()):
			print("user is not verifiable")
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')

	if request.method == "POST":
		email_code = request.POST["email_code"]
		if verify_email_code(request.user, email_code):
			return redirect('root_index')
		else:
			messages.info(request, "Wrong code, please try again")

	__x = timezone.now() - datetime.timedelta(seconds = settings.EMAIL_VERIFICATION_SEND_TIMEOUT)
	seconds_left = 0
	if request.user.verification_sent_date > __x:
		seconds_left = settings.EMAIL_VERIFICATION_SEND_TIMEOUT - math.floor((timezone.now() - request.user.verification_sent_date).total_seconds())

	return render(request, 'account/verify_email.html', {
		"retry_seconds_left" : seconds_left
	})

def signup(request):
	if request.user.is_authenticated:
		if not request.user.is_verified:
			if not (request.user.is_verifiable()):
				user = request.user
				auth.logout(request)
				user.delete()
				return redirect('root_index')

			return redirect('account:verify_email')
		return redirect('root_index')
	
	if request.method == "POST":
		__email      = request.POST["email"]
		__username   = request.POST["username"]
		__password_1 = request.POST["password"]
		__password_2 = request.POST["password2"]

		if len(__password_1) < 8:
			messages.info(request, "Password should contain at least 8 characters")
			return redirect('account:signup')

		if __password_1 != __password_2:
			messages.info(request, "Passwords don't match")
			return redirect('account:signup')

		if UserAccount.objects.filter(username = __username).exists():
			messages.info(request, "User with username \"" + __username + "\" already exists")
			return redirect('account:signup')
		elif UserAccount.objects.filter(email = __email).exists():
			messages.info(request, "Email \"" + __email + "\" is already being used")
			return redirect('account:signup')

		user = UserAccount.objects.create_user(email = __email, username = __username, password = __password_1,
			# Disable user until they are verified
			is_verified = False)

		send_email_verification_code(user)

		user.save()

		auth.login(request, user)
		return redirect('account:verify_email')

		# return redirect('root_index')

	if request.method == "GET":
		return render(request, 'account/signup.html')

def logout(request):
	if request.user.is_authenticated:
		if not (request.user.is_verifiable()):
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')

		auth.logout(request)
		
	return redirect('root_index')

def profile(request):
	if not request.user.is_authenticated:
		return redirect('root_index')

	if not request.user.is_verified:
		if not (request.user.is_verifiable()):
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')

		return redirect('account:verify_email')

	return render(request, 'account/profile.html')

@csrf_exempt
def update_profile(request):
	if (request.method != "POST"):
		return redirect('account:profile')

	if not request.user.is_authenticated:
		return redirect('root_index')

	if not request.user.is_verified:
		if not (request.user.is_verifiable()):
			user = request.user
			auth.logout(request)
			user.delete()
			return redirect('root_index')

		return redirect('account:verify_email')

	__username = request.POST.get("username", None)
	__darktheme = request.POST.get("darktheme", False)

	if __darktheme == "on":
		__darktheme = True

	if not __username:
		return HttpResponse(status = 500)

	update = False

	if __username != request.user.username:
		if UserAccount.objects.filter(username = __username).exists():
			messages.info(request, "User with this username already exists")
		else:
			request.user.username = __username
			update = True

	if __darktheme != request.user.dark_theme:
		request.user.dark_theme = __darktheme
		update = True

	if update:
		messages.info(request, "Your profile was successfully updated!")
		request.user.save()
		
	return redirect('account:profile')
