from django.urls import path, include

from . import views

app_name = "account"

urlpatterns = [
	path('login/', views.login, name = "login"),
	path('signup/', views.signup, name = "signup"),
	path('verify_email/', views.verify_email, name = "verify_email"),
	path('send_verification_code', views.send_verification_code, name = "send_verification_code"),
	path('logout/', views.logout, name = "logout"),

	path('profile/', views.profile, name = "profile"),
	path('update_profile', views.update_profile, name = "update_profile"),
]