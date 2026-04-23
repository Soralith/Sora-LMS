import json
import urllib.request
import urllib.error
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import AISettings


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