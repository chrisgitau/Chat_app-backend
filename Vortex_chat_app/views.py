from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from .models import ChatRoom
from .serializers import ChatRoomSerializer, UserSerializer, SignupSerializer
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm  # Ensure these forms are defined in forms.py
from rest_framework.views import APIView
from rest_framework import status

# Chat Room View
@login_required
def chat_room(request, room_name):
    room, created = ChatRoom.objects.get_or_create(name=room_name)
    serializer = ChatRoomSerializer(room)
    return JsonResponse(serializer.data)

# Create Chat Room View
@csrf_exempt
def create_chatroom(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Default Chat Room')
        chatroom, created = ChatRoom.objects.get_or_create(name=name)
        serializer = ChatRoomSerializer(chatroom)
        if created:
            return JsonResponse({'message': 'ChatRoom created successfully.', 'data': serializer.data})
        else:
            return JsonResponse({'message': 'ChatRoom already exists.', 'data': serializer.data}, status=400)
    elif request.method == 'GET':
        return render(request, 'create_chatroom.html')
    else:
        return HttpResponseBadRequest('Invalid request method.')

# Create Default Chat Room View
@login_required
def create_default_chatroom(request):
    return render(request, 'default_chatroom.html')

# Index View
def index(request):
    return render(request, 'index.html')

# Signup View
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create_default_chatroom')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# Login View
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('create_default_chatroom')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Logout View
def user_logout(request):
    logout(request)
    return redirect('login')

# API to Get Chat Room Details
@login_required
def api_get_chat_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    serializer = ChatRoomSerializer(room)
    return JsonResponse(serializer.data)

# API to List All Chat Rooms
@login_required
def api_list_chat_rooms(request):
    rooms = ChatRoom.objects.all()
    serializer = ChatRoomSerializer(rooms, many=True)
    return JsonResponse(serializer.data, safe=False)

# API to Create Chat Room
@csrf_exempt
def api_create_chatroom(request):
    if request.method == 'POST':
        name = request.POST.get('name', 'Default Chat Room')
        chatroom, created = ChatRoom.objects.get_or_create(name=name)
        serializer = ChatRoomSerializer(chatroom)
        if created:
            return JsonResponse({'message': 'ChatRoom created successfully.', 'data': serializer.data})
        else:
            return JsonResponse({'message': 'ChatRoom already exists.', 'data': serializer.data}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=405)

# API for User Signup
@csrf_exempt
class Signup(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# API for User Login
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from .forms import LoginForm

@csrf_exempt
def api_user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = LoginForm(data)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    return JsonResponse({'message': 'User logged in successfully.'})
                else:
                    return JsonResponse({'message': 'Invalid credentials.'}, status=400)
            else:
                return JsonResponse({'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON.'}, status=400)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=405)

# API for User Logout
@login_required
def api_user_logout(request):
    logout(request)
    return JsonResponse({'message': 'User logged out successfully.'})
