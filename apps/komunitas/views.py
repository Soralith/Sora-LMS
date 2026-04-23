from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import KomunitasMessage


@login_required
def index(request):
    kom_msgs = KomunitasMessage.objects.select_related('user')[:50]
    return render(request, 'komunitas/index.html', {
        'messages': kom_msgs,
    })


@login_required
def message_list(request):
    kom_msgs = KomunitasMessage.objects.select_related('user')[:50]
    return render(request, 'komunitas/partials/message_list.html', {
        'messages': kom_msgs,
    })


@login_required
def post_message(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if content or image:
            KomunitasMessage.objects.create(
                user=request.user,
                content=content,
                image=image
            )
    
    return HttpResponse(status=200)