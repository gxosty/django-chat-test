from django.shortcuts import render, redirect

from django.http import HttpResponse

def index(request):
	if (request.user.is_authenticated):
		return redirect('chat:index')

	return render(request, "root_index.html")