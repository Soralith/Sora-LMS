import json
import urllib.request
import urllib.error
from datetime import datetime
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import AISettings
from apps.courses.models import Course, Enrollment, MaterialProgress, Announcement, Material, Module
from apps.quizzes.models import Quiz, QuizAttempt
from apps.assignments.models import Assignment, Submission
from apps.accounts.models import User


@login_required
def chat_view(request):
    return render(request, 'ai_chat/chat.html')


@login_required
@require_POST
def chat_api(request):
    try:
        body = json.loads(request.body)
        messages = body.get('messages', [])

        if not messages:
            return JsonResponse({'error': 'Pesan kosong.'}, status=400)

        # Get settings from database
        ai_settings = AISettings.get_active_settings()
        
        # Use API key from settings or fall back to settings.GEMINI_API_KEY
        api_key = ai_settings.gemini_api_key if ai_settings and ai_settings.gemini_api_key else getattr(settings, 'GEMINI_API_KEY', '')
        
        if not api_key:
            return JsonResponse({'error': 'API key Gemini belum dikonfigurasi.'}, status=500)

        # Get system instruction from database or use default
        system_instruction = ai_settings.system_instruction if ai_settings else (
            'Kamu adalah asisten AI di Sora LMS, sebuah platform pembelajaran online. '
            'Bantu siswa, guru, dan admin dengan pertanyaan seputar pembelajaran, materi pelajaran, '
            'dan penggunaan platform. Jawab dalam Bahasa Indonesia yang ramah dan jelas.'
        )

        # Build Gemini contents
        contents = []
        for msg in messages:
            role = 'user' if msg['role'] == 'user' else 'model'
            contents.append({
                'role': role,
                'parts': [{'text': msg['content']}]
            })

        payload = json.dumps({
            'contents': contents,
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 2048,
            },
            'systemInstruction': {
                'parts': [{'text': system_instruction}]
            }
        }).encode('utf-8')

        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        reply = result['candidates'][0]['content']['parts'][0]['text']
        return JsonResponse({'reply': reply})

    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode('utf-8'))
        return JsonResponse({'error': err.get('error', {}).get('message', 'Gagal menghubungi Gemini.')}, status=502)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def live_data_api(request):
    data_type = request.GET.get('type', '')
    user = request.user

    result = {'timestamp': datetime.now().isoformat(), 'data': {}}

    if data_type in ('all', 'enrollments'):
        enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course')
        result['data']['enrollments'] = [
            {
                'course_id': e.course.id,
                'course_title': e.course.title,
                'progress': e.progress,
                'enrolled_at': e.enrolled_at.isoformat() if e.enrolled_at else None,
            }
            for e in enrollments
        ]

    if data_type in ('all', 'progress'):
        material_progress = MaterialProgress.objects.filter(student=user, is_completed=True)
        result['data']['completed_materials'] = [
            {
                'material_id': mp.material.id,
                'material_title': mp.material.title,
                'completed_at': mp.completed_at.isoformat() if mp.completed_at else None,
            }
            for mp in material_progress.select_related('material', 'material__module', 'material__module__course')[:50]
        ]

    if data_type in ('all', 'announcements'):
        course_ids = Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True)
        announcements = Announcement.objects.filter(course_id__in=course_ids).select_related('course', 'author')[:20]
        result['data']['announcements'] = [
            {
                'id': a.id,
                'course_title': a.course.title,
                'title': a.title,
                'content': a.content[:200],
                'created_at': a.created_at.isoformat() if a.created_at else None,
            }
            for a in announcements
        ]

    if data_type in ('all', 'quiz_scores'):
        attempts = QuizAttempt.objects.filter(student=user, status='completed').select_related('quiz', 'quiz__course')
        result['data']['quiz_attempts'] = [
            {
                'quiz_title': a.quiz.title,
                'course_title': a.quiz.course.title,
                'score': float(a.score) if a.score else None,
                'percentage': float(a.percentage) if a.percentage else None,
                'passed': a.is_passed(),
                'completed_at': a.completed_at.isoformat() if a.completed_at else None,
            }
            for a in attempts[:20]
        ]

    if data_type in ('all', 'assignments'):
        submissions = Submission.objects.filter(student=user).select_related('assignment', 'assignment__course')
        result['data']['assignments'] = [
            {
                'assignment_title': s.assignment.title,
                'course_title': s.assignment.course.title,
                'due_date': s.assignment.due_date.isoformat() if s.assignment.due_date else None,
                'is_overdue': s.assignment.is_overdue(),
                'status': s.status,
                'score': float(s.score) if s.score else None,
                'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
            }
            for s in submissions[:20]
        ]

    if data_type in ('all', 'courses'):
        courses = Course.objects.filter(status='active').only('id', 'title', 'description', 'category__name')[:50]
        course_enroll_ids = set(Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True))
        result['data']['available_courses'] = [
            {
                'id': c.id,
                'title': c.title,
                'description': c.description[:150],
                'category': c.category.name if c.category else None,
                'is_enrolled': c.id in course_enroll_ids,
            }
            for c in courses.select_related('category')
        ]

    return JsonResponse(result)