import re
from django.shortcuts import render,redirect,HttpResponse, get_object_or_404
from urllib.parse import unquote
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from .serializers import StateSerializer


def index(request):
    error = None
    user = request.user
    user_rooms = None
    if user.is_authenticated:
        user_rooms = Room.objects.filter(user=user)
    if request.method == 'POST':
        create_room = request.POST.get('create_room', None)
        if create_room:
            name = request.POST.get('name', 'default')
            if 3 <= len(name) <= 50:
                if re.match("^[a-zA-Z0-9_ ]*$",name):
                    if not Room.objects.filter(name=name).exists():
                        new_room = Room(name=name, slug=name.replace(' ', '-'))
                        new_room.save()

                        new_current = CurrentState(room=new_room)
                        new_current.save()
                        return redirect('jb:manage', new_room.pk)
                    else:
                        error = 'Room with this name already exists.'
                else:
                    error = 'No special / region specific characters allowed. (Use: a-Z, spaces, underscores.)'
            else:
                error = 'Name of the room has to consist of 3 to 50 characters.'

        # claim room form is available for logged users
        claim_room = request.POST.get('claim_room', None)
        if claim_room and user.is_authenticated:
            claim_room_id = request.POST.get('claim_room_id')
            try:
                room = Room.objects.get(id=claim_room_id)
                room.user = user
                room.save()
            except:
                error = 'Room with this ID doesn\'t exists'

    return render(request, 'JukeBox/index.html', {'error': error, 'user_rooms': user_rooms})


def listen(request, room_slug):
    room = get_object_or_404(Room, slug=unquote(room_slug))
    state = get_object_or_404(CurrentState, room=room)
    return render(request,'JukeBox/listener.html', {'room': room, 'state': state})


def manage(request, room_id):
    try:
        room = get_object_or_404(Room, id=room_id)
    except:
        return HttpResponse('404')
    user = request.user
    if room.user and room.user != user:
        return HttpResponse('This room is claimed. If it\'s yours then log-in.')
    room_state = CurrentState.objects.get(room=room)
    room_videos = Video.objects.filter(room=room)
    error = None

    # turn on autoescape in template
    if not room.user:
        error = 'Right now everyone who has url to this room can enter and mess with controls.' \
                '<br> If you want to prevent this, you can log-in and claim this room using following id: ' + str(room.pk)
    if request.method == 'POST':

        # plays video form list (starts from beginning)
        video = request.POST.get('video', None)
        if video:
            try:
                video = Video.objects.get(id=int(video))
            except:
                error = 'Well... This video doesn\'t exists..'
            room_state.video = video
            room_state.paused = False
            room_state.play_pause_count += 1
            room_state.time = 0
            room_state.save()

        # play/pause button control
        status = request.POST.get('status', None)
        if status:
            if status == 'play':
                room_state.paused = False
            else:
                room_state.paused = True
            room_state.play_pause_count += 1
            room_state.save()

        # forward/rewind control
        time = request.POST.get('time', None)
        if time:
            try:
                time = request.POST.get('time_value', 0)
                time = time.split(':')
                room_state.time = int(time[0]) * 3600 + int(time[1]) * 60 + int(time[2])
                room_state.rewind_count += 1
                room_state.save()
            except:
                error = 'Hey you! Don\'t mess with my HTML.'

        # adds new video to the list
        add_video = request.POST.get('add_video_button', None)
        if add_video:
            add_video_name = request.POST.get('video_name', 'new video')
            add_video_url = request.POST.get('video_url', 'dQw4w9WgXcQ')
            if len(add_video_url) == 11 and re.match("[a-zA-Z0-9_\-]*$", add_video_url) and len(add_video_name) > 0:

                add_video = Video(room=room, name=add_video_name, url=add_video_url)
                add_video.save()
            else:
                error = add_video_url + ' isn\'t valid YouTube video ID.'

        # deletes video from the list
        delete = request.POST.get('delete', None)
        if delete:
            try:
                delete_video = room_videos.get(pk=int(delete))
                delete_video.delete()
            except:
                error = 'That\'s strange... You tried to delete video that doesn\'t exists.'

    context = {'room_videos': room_videos, 'state': room_state, 'room': room, 'error': error}

    return render(request,'JukeBox/admin.html', context)


class CurrentStateView(APIView):

    def get(self, request, room_slug):
        room = get_object_or_404(Room, slug=room_slug)
        current_state = get_object_or_404(CurrentState, room=room)
        serializer = StateSerializer(current_state, many=False)
        return Response(serializer.data)

    def post(self):
        pass


def register(request):
    if request.user.is_authenticated:
        return redirect('jb:index')

    message = None
    if request.method == 'POST':
        username = request.POST.get('login','nic')
        password = request.POST.get('password','nic')
        r_password = request.POST.get('r_password','nic1')
        mail = request.POST.get('email', 'abc@example.com')

        if len(username) >= 4 and username.find(' ') == -1:
            if len(password) >= 5:
                if password == r_password:
                    if not User.objects.filter(username__iexact=username).exists():
                        user = User.objects.create_user(username, mail, password)  # creates user
                        user = authenticate(request, username=username, password=password)
                        if user is not None:
                            login(request, user)
                            return redirect('jb:index')
                    else:
                        message = 'Username already taken.'
                else:
                    message = 'Passwords don\'t match.'
            else:
                message = 'Password have to consist of minimum 5 characters.'
        else:
            message = 'Username has to at least 4 characters long + no spaces allowed.'
    return render(request, 'JukeBox/register.html', {'message': message})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('jb:index')
    message = None
    if request.method == 'POST':
        username = request.POST.get('login', 'a')
        password = request.POST.get('password', 'a')
        try:
            user = User.objects.get(username__iexact=username)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('jb:index')
            else:
                message = 'Wrong username-password combination.'
        except ObjectDoesNotExist:
            message = 'Wrong username-password combination.'
    return render(request, 'JukeBox/login.html', {'message': message})


def logout_view(request):
    logout(request)
    return redirect('jb:index')


def contact(request):
    message = None
    if request.method == 'POST':
        subject = request.POST.get('subject','no subject')
        email = request.POST.get('email', 'no email')
        content = request.POST.get('content', 'no content') + '\nemail: '+ email
        try:
            send_mail(subject,content,'zyvik.kontakt@wp.pl',['pawel86gw2@gmail.com'])
            message = 'Mail sent!'
        except:
            message = 'Something broke - send me an email at: pawel86@gmail.com'

    return render(request, 'JukeBox/contact.html', {'message': message})
