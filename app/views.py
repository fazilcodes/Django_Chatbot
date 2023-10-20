from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
import openai

from dotenv import load_dotenv
import os
load_dotenv()

from .models import Chat
from django.utils import timezone


open_ai_key = os.environ.get('OPENAI_KEY')
openai.api_key = open_ai_key

def chat_openai(message):
    # text completion Model davinci
    # response = openai.Completion.create(
    #     model = 'text-davinci-003',
    #     prompt = message,
    #     max_tokens = 150,
    #     n = 1,
    #     stop = None,
    #     temperature = 0.7,
    # )
    # answer = response.choices[0].text.strip()
    # return answer

    #gpt-3 turbo Chat completion Model 
    response = openai.ChatCompletion.create(
        model = 'gpt-3.5-turbo',
        messages = [
            {"role": "system", "content": "You are an helpful assistant"},
            {"role": "user", "content": message},
        ]
    )
    answer = response.choices[0].message.content.strip()
    return answer

# Create your views here.

def home(req):
    chats = None
    if req.method == 'POST':
        message = req.POST.get('message')
        response = chat_openai(message)

        if req.user.is_authenticated:
            chat = Chat(user=req.user, message=message, response=response, created_at=timezone.now())
            chat.save()

        return JsonResponse({'message': message, 'response': response})

    if req.user.is_authenticated:
        chats = Chat.objects.filter(user=req.user)

    context = {
        'chats': chats
    }

    return render(req, 'index.html', context)

def register(req):
    error_message = None

    if req.method == 'POST':
        username = req.POST.get('username')
        email = req.POST.get('email')
        password1 = req.POST.get('password1')
        password2 = req.POST.get('password2')

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(req, user)
                return redirect('home')
            except:
                error_message = 'Error creating account'
        else:
            error_message = "password doesn't match"
        
    context = {
        'error_message': error_message
    }
    return render(req, 'login.html', context)

def login(req):
    error_login = None
    if req.method == 'POST':
        username = req.POST.get('username')
        password = req.POST.get('password')

        user = auth.authenticate(req, username=username, password=password)
        if user is not None:
            auth.login(req, user)
            return redirect('home')
        else:
            error_login = 'invalid credentials'

    context = {
        'error_login': error_login
    }
    return render(req, 'login.html', context)

def logout(req):
    auth.logout(req)
    return redirect('login')