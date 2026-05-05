from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import KomunitasMessage
from apps.courses.models import Course, Enrollment


@login_required
def index(request):
    kom_msgs = KomunitasMessage.objects.filter(course__isnull=True).select_related('user').order_by('-created_at')
    return render(request, 'komunitas/index.html', {
        'messages': kom_msgs,
    })


@login_required
def message_list(request):
    kom_msgs = KomunitasMessage.objects.filter(course__isnull=True).select_related('user').order_by('-created_at')
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


def _check_course_access(request, course):
    """Check if user has access to course community. Returns True if authorized."""
    if request.user.is_admin:
        return True
    if course.is_teacher_of(request.user):
        return True
    if request.user.is_student and Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        return True
    return False


@login_required
def course_community(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not _check_course_access(request, course):
        messages.error(request, 'Anda tidak memiliki akses ke komunitas kelas ini.')
        return redirect('courses:course_detail', slug=slug)

    kom_msgs = KomunitasMessage.objects.filter(course=course).select_related('user').order_by('-created_at')
    return render(request, 'komunitas/course_community.html', {
        'course': course,
        'messages': kom_msgs,
    })


@login_required
def course_community_message_list(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not _check_course_access(request, course):
        return HttpResponse(status=403)

    kom_msgs = KomunitasMessage.objects.filter(course=course).select_related('user').order_by('-created_at')
    return render(request, 'komunitas/partials/message_list.html', {
        'messages': kom_msgs,
    })


@login_required
def course_community_post_message(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not _check_course_access(request, course):
        return HttpResponse(status=403)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')

        if content or image:
            KomunitasMessage.objects.create(
                user=request.user,
                course=course,
                content=content,
                image=image
            )
    
    return HttpResponse(status=200)