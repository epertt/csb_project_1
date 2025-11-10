from datetime import datetime
import sqlite3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import DiaryEntry
#import logging

def index(request):
    if request.user.is_authenticated:
        return redirect('/diary')
    return redirect('/login')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if password != password2: 
            return render(request, 'register.html', {'error': 'passwords do not match'})
        if User.objects.filter(username=username).exists(): 
            return render(request, 'register.html', {'error': 'user already exists'})

        # A02:      cryptographic failures
        # problem:  passwords stored in plaintext in database
        # fix:      use django's built in user creation which automatically hashes passwords
        # A03:      injection 
        # problem:  user can enter a username or password that breaks out of the SQL string using quotes (e.g., ' OR '1'='1)
        # fix:      use django's built in user creation or at least parameterized queries
        
        cursor = sqlite3.connect('db.sqlite3').cursor()
        sql = f"INSERT INTO auth_user(password, username, first_name, last_name, is_superuser, is_staff, is_active, email, date_joined) VALUES('{password}', '{username}', '', '', 0, 0, 1, '', '{current_date}')"
        cursor.execute(sql)
        cursor.connection.commit()
        cursor.close()
        user = User.objects.get(username=username)

        # fix: comment out everything between the last comment and this comment before uncommenting the next line
        #user = User.objects.create_user(username=username, password=password)

        login(request, user)
        return redirect('/diary')
    
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # A03:      injection
        # problem:  user can enter a username or password that breaks out of the SQL string using quotes (e.g., ' OR '1'='1)
        # fix:      use django's built in authentication or at least parameterized queries instead

        cursor = sqlite3.connect('db.sqlite3').cursor()
        sql = f"SELECT * FROM auth_user WHERE username='{username}' AND password='{password}'"
        user = cursor.execute(sql).fetchone()
        #user = authenticate(request, username=username, password=password)

        if user is not None:
            user = User.objects.get(username=username)
            login(request, user)
            return redirect('/diary')
        else:
            # A09:      security logging and monitoring failures
            # problem:  failed login attempts not logged -> brute force attacks undetectable
            # fix:      add logging
            #
            # note: only logs to stdout; logging to a file would generally be a better choice
            # logger = logging.getLogger(__name__); logger.warning(f'{datetime.now()}: \!/ failed login by user: {username} from IP: {request.META.get("REMOTE_ADDR")} \!/')
            return render(request, 'login.html', {'error': 'user doesn\'t exist or bad password'})
    
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login')


@login_required(login_url='/login')
def diary_view(request):
    entries = DiaryEntry.objects.filter(user=request.user)
    
    return render(request, 'diary.html', {
        'username': request.user.username,
        'uid': request.user.id,
        'entries': entries
    })


@login_required(login_url='/login')
def add_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        DiaryEntry.objects.create(
            user=request.user,
            title=title,
            content=content
        )
        return redirect('/diary')
    
    return render(request, 'add.html')


@login_required(login_url='/login')
def read_view(request, entry_id):
    # A01:      broken access control 
    # problem:  any user can read any diary entry by going to http://url:port/read/<id>
    # fix:      add user check after id=entry_id

    entry = get_object_or_404(DiaryEntry, id=entry_id)
    #entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    return render(request, 'read.html', {'entry': entry})


@login_required(login_url='/login')
def edit_view(request, entry_id):
    # A01:      broken access control
    # problem:  any user can edit any diary entry by going to http://url:port/edit/<id>
    # fix:      add user check after id=entry_id

    entry = get_object_or_404(DiaryEntry, id=entry_id)
    #entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)

    if request.method == 'POST':
        entry.title = request.POST.get('title')
        entry.content = request.POST.get('content')
        entry.save()
        return redirect(f'/read/{entry_id}')
    
    return render(request, 'edit.html', {'entry': entry})


@login_required(login_url='/login')
def delete_view(request, entry_id):
    # A01:      broken access control
    # problem:  any user can delete any diary entry by going to http://url:port/delete/<id>
    # fix:      add user check after id=entry_id
    # fix_ex:   entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)

    entry = get_object_or_404(DiaryEntry, id=entry_id)
    #entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    entry.delete()
    return redirect('/diary')


@login_required(login_url='/login')
def profile_view(request):
    # A01:      broken access control
    # problem:  any user can view any profile by going to http://url:port/profile?uid=<id>
    # fix:      get uid from request.user.id instead of the url

    uid = request.GET.get('uid')
    #uid = request.user.id
    user = get_object_or_404(User, id=uid)
    entry_count = DiaryEntry.objects.filter(user=user).count()
    entries = DiaryEntry.objects.filter(user=user)
    
    return render(request, 'profile.html', {
        'user': user,
        'entry_count': entry_count,
        'entries': entries
    })