from django.urls import path, include

from . import views

app_name = "chat"

urlpatterns = [
	path('', views.index, name = "index"),
	path('search_user', views.search_user, name = "search_user"),
	path('get_chats', views.get_chats, name = "get_chats")
]