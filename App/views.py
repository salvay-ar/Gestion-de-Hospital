from django.http import HttpResponse
from django.shortcuts import render, HttpResponseRedirect


from django.shortcuts import render

def inicio(request):
    return render(request, "App/inicio.html")

def login(request):
    return render(request, "App/login.html")