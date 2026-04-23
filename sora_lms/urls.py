from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect, render
from django.views.static import serve


def landing_page(request):
    return render(request, 'landing_page/index.html')


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
