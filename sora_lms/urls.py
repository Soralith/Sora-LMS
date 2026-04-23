from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from django.views.static import serve

from apps.accounts.models import User
from apps.courses.models import Course, Enrollment, Module
from apps.quizzes.models import Quiz
from apps.assignments.models import Assignment, Submission


def landing_page(request):
    # Public stats (visible to all)
    stats = {
        'total_users': User.objects.count(),
        'total_courses': Course.objects.count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_quizzes': Quiz.objects.count(),
        'total_assignments': Assignment.objects.count(),
    }
    
    # User-specific dashboard data
    dashboard_data = None
    if request.user.is_authenticated:
        user = request.user
        if user.role == 'student':
            enrollments = Enrollment.objects.filter(student=user).select_related('course')
            completed = Submission.objects.filter(student=user, score__isnull=False).count()
            courses_list = []
            for e in enrollments[:3]:
                prog = int(e.progress * 100)
                if prog > 100: prog = 100
                courses_list.append({'name': e.course.title, 'progress': prog})
            dashboard_data = {
                'name': user.get_full_name() or user.username,
                'kelas_diikuti': enrollments.count(),
                'tugas_selesai': completed,
                'courses': courses_list
            }
        elif user.role == 'teacher':
            courses = Course.objects.filter(teacher=user)
            submissions = Submission.objects.filter(assignment__course__teacher=user, score__isnull=False).count()
            courses_list = []
            for c in courses[:3]:
                courses_list.append({'name': c.title, 'students': c.enrollments.count()})
            dashboard_data = {
                'name': user.get_full_name() or user.username,
                'kelas_diajar': courses.count(),
                'tugas_dinilai': submissions,
                'courses': courses_list
            }
        elif user.role == 'admin':
            from django.utils import timezone
            from datetime import timedelta
            week_ago = timezone.now() - timedelta(days=7)
            recent_users = User.objects.filter(date_joined__gte=week_ago).count()
            recent_courses = Course.objects.filter(created_at__gte=week_ago).count()
            pending_score = Submission.objects.filter(score__isnull=True, status='submitted').count()
            dashboard_data = {
                'name': user.get_full_name() or user.username,
                'total_users': User.objects.count(),
                'total_courses': Course.objects.count(),
                'total_teachers': User.objects.filter(role='teacher').count(),
                'total_students': User.objects.filter(role='student').count(),
                'recent_users': recent_users,
                'recent_courses': recent_courses,
                'pending_score': pending_score,
            }
    
    return render(request, 'landing_page/index.html', {'stats': stats, 'dashboard': dashboard_data})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', landing_page, name='home'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('courses/', include('apps.courses.urls', namespace='courses')),
    path('assignments/', include('apps.assignments.urls', namespace='assignments')),
    path('quizzes/', include('apps.quizzes.urls', namespace='quizzes')),
    # Serve media files eksplisit
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('ai-chat/', include('apps.ai_chat.urls', namespace='ai_chat')),
    path('komunitas/', include('apps.komunitas.urls', namespace='komunitas')),
]

# Tambahan serve media saat DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site header
admin.site.site_header = "Sora LMS Admin"
admin.site.site_title = "Sora LMS"
admin.site.index_title = "Panel Administrasi Sora LMS"
