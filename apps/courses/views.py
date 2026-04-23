from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Q
from .models import Course, Module, Material, Enrollment, MaterialProgress, Category, Announcement, MaterialComment
from .forms import CourseForm, ModuleForm, MaterialForm, AnnouncementForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.timesince import timesince
import json
import uuid


@login_required
def course_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    if request.user.is_admin:
        courses = Course.objects.all()
    elif request.user.is_teacher:
        # Guru lihat semua kelas
        courses = Course.objects.all()
    else:
        # Siswa: hanya tampilkan kelas yang dia di-enroll
        enrolled_ids = list(Enrollment.objects.filter(
            student=request.user, is_active=True
        ).values_list('course_id', flat=True))
        courses = Course.objects.filter(id__in=enrolled_ids)

    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        courses = courses.filter(category_id=category_id)

    categories = Category.objects.all()

    # Untuk siswa, tandai kelas mana saja yang sudah dienroll
    enrolled_ids = []
    if request.user.is_student:
        enrolled_ids = list(Enrollment.objects.filter(
            student=request.user, is_active=True
        ).values_list('course_id', flat=True))

    # Untuk guru, tandai kelas yang dia ajar
    my_course_ids = []
    if request.user.is_teacher:
        my_course_ids = list(Course.objects.filter(
            Q(teacher=request.user) | Q(teachers=request.user)
        ).values_list('id', flat=True))

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'query': query,
        'categories': categories,
        'category_id': category_id,
        'enrolled_ids': enrolled_ids,
        'my_course_ids': my_course_ids,
    })


@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment = None
    is_enrolled = False

    if request.user.is_student:
        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_enrolled = enrollment is not None and enrollment.is_active

        if not is_enrolled and course.status != 'active':
            messages.error(request, 'Kelas ini tidak tersedia.')
            return redirect('courses:course_list')

    modules = course.modules.prefetch_related('materials').all()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'enrollment': enrollment,
        'is_enrolled': is_enrolled,
        'is_teacher': course.is_teacher_of(request.user),
        'announcements': course.announcements.all()[:5],
    })


@login_required
def course_create(request):
    if not (request.user.is_teacher or request.user.is_admin):
        messages.error(request, 'Hanya guru yang dapat membuat kelas.')
        return redirect('courses:course_list')

    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            base_slug = slugify(course.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            course.slug = slug
            course.save()
            messages.success(request, 'Kelas berhasil dibuat!')
            return redirect('courses:course_detail', slug=course.slug)

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Buat'})


@login_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Kelas berhasil diperbarui!')
            return redirect('courses:course_detail', slug=course.slug)

    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


@login_required
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Kelas berhasil dihapus.')
        return redirect('courses:course_list')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
def manage_enrollments(request, slug):
    """Halaman kelola pendaftaran siswa — hanya admin/guru"""
    course = get_object_or_404(Course, slug=slug)
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=slug)

    from apps.accounts.models import User
    # Siswa yang belum terdaftar di kelas ini
    enrolled_student_ids = Enrollment.objects.filter(
        course=course, is_active=True
    ).values_list('student_id', flat=True)
    available_students = User.objects.filter(role='student').exclude(id__in=enrolled_student_ids)
    enrollments = Enrollment.objects.filter(course=course, is_active=True).select_related('student')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            student_ids = request.POST.getlist('student_ids')
            added = 0
            for sid in student_ids:
                student = User.objects.filter(pk=sid, role='student').first()
                if student:
                    Enrollment.objects.get_or_create(student=student, course=course, defaults={'is_active': True})
                    added += 1
            messages.success(request, f'{added} siswa berhasil didaftarkan ke kelas ini.')
            return redirect('courses:manage_enrollments', slug=slug)

        elif action == 'remove':
            enrollment_id = request.POST.get('enrollment_id')
            enrollment = Enrollment.objects.filter(pk=enrollment_id, course=course).first()
            if enrollment:
                enrollment.delete()
                messages.success(request, f'{enrollment.student.get_full_name() or enrollment.student.username} berhasil dikeluarkan dari kelas.')
            return redirect('courses:manage_enrollments', slug=slug)

    return render(request, 'courses/manage_enrollments.html', {
        'course': course,
        'enrollments': enrollments,
        'available_students': available_students,
    })


@login_required
def assign_teachers(request, slug):
    """Admin assign guru ke kelas"""
    if not request.user.is_admin:
        messages.error(request, 'Hanya admin yang dapat mengatur guru.')
        return redirect('courses:course_list')

    course = get_object_or_404(Course, slug=slug)
    from apps.accounts.models import User
    all_teachers = User.objects.filter(role='teacher').order_by('first_name', 'username')

    if request.method == 'POST':
        selected_ids = request.POST.getlist('teacher_ids')
        course.teachers.set(selected_ids)
        messages.success(request, 'Guru pengajar berhasil diperbarui.')
        return redirect('courses:course_detail', slug=slug)

    assigned_ids = list(course.teachers.values_list('id', flat=True))
    return render(request, 'courses/assign_teachers.html', {
        'course': course,
        'all_teachers': all_teachers,
        'assigned_ids': assigned_ids,
    })

@login_required
def module_create(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=slug)

    form = ModuleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, 'Modul berhasil ditambahkan!')
        return redirect('courses:course_detail', slug=slug)

    return render(request, 'courses/module_form.html', {'form': form, 'course': course, 'action': 'Tambah'})


@login_required
def module_edit(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if not (module.course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = ModuleForm(request.POST or None, instance=module)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Modul berhasil diperbarui!')
        return redirect('courses:course_detail', slug=module.course.slug)

    return render(request, 'courses/module_form.html', {
        'form': form, 'course': module.course, 'module': module, 'action': 'Edit'
    })


@login_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    course = module.course
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Modul berhasil dihapus.')
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def material_create(request, module_pk):
    module = get_object_or_404(Module, pk=module_pk)
    if not (module.course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = MaterialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        material = form.save(commit=False)
        material.module = module
        material.save()
        messages.success(request, 'Materi berhasil ditambahkan!')
        return redirect('courses:course_detail', slug=module.course.slug)

    return render(request, 'courses/material_form.html', {
        'form': form, 'module': module, 'action': 'Tambah'
    })


@login_required
def material_detail(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.module.course

    is_completed = False
    if request.user.is_student:
        enrollment = get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
        progress, _ = MaterialProgress.objects.get_or_create(
            student=request.user, material=material
        )
        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()
            update_course_progress(request.user, course)
        is_completed = progress.is_completed

    comments = MaterialComment.objects.filter(
        material=material, parent=None
    ).select_related('author').prefetch_related('replies__author')

    return render(request, 'courses/material_detail.html', {
        'material': material,
        'course': course,
        'is_teacher': course.is_teacher_of(request.user),
        'is_completed': is_completed,
        'comments': comments,
    })


@login_required
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if not (material.module.course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = MaterialForm(request.POST or None, request.FILES or None, instance=material)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Materi berhasil diperbarui!')
        return redirect('courses:course_detail', slug=material.module.course.slug)

    return render(request, 'courses/material_form.html', {
        'form': form, 'module': material.module, 'material': material, 'action': 'Edit'
    })


@login_required
def material_delete(request, pk):
    material = get_object_or_404(Material, pk=pk)
    course = material.module.course
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        material.delete()
        messages.success(request, 'Materi berhasil dihapus.')
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def announcement_create(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not (course.is_teacher_of(request.user) or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=slug)

    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ann = form.save(commit=False)
        ann.course = course
        ann.author = request.user
        ann.save()
        messages.success(request, 'Pengumuman berhasil diterbitkan!')
        return redirect('courses:course_detail', slug=slug)

    return render(request, 'courses/announcement_form.html', {'form': form, 'course': course})


def update_course_progress(student, course):
    total_materials = Material.objects.filter(
        module__course=course, is_published=True
    ).count()
    if total_materials == 0:
        return
    completed = MaterialProgress.objects.filter(
        student=student,
        material__module__course=course,
        is_completed=True
    ).count()
    progress = (completed / total_materials) * 100
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if enrollment:
        enrollment.progress = round(progress, 2)
        if progress >= 100:
            enrollment.completed_at = timezone.now()
        enrollment.save()

@login_required
@require_POST
def comment_add(request, material_pk):
    material = get_object_or_404(Material, pk=material_pk)
    course = material.module.course
 
    # Cek akses: harus enrolled atau guru/admin
    if request.user.is_student:
        if not Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
            return JsonResponse({'error': 'Akses ditolak.'}, status=403)
 
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Request tidak valid.'}, status=400)
 
    content = body.get('content', '').strip()
    parent_id = body.get('parent_id')
 
    if not content:
        return JsonResponse({'error': 'Komentar tidak boleh kosong.'}, status=400)
    if len(content) > 2000:
        return JsonResponse({'error': 'Komentar terlalu panjang (maks 2000 karakter).'}, status=400)
 
    parent = None
    if parent_id:
        parent = get_object_or_404(MaterialComment, pk=parent_id, material=material, parent=None)
 
    comment = MaterialComment.objects.create(
        material=material,
        author=request.user,
        parent=parent,
        content=content,
    )
 
    user = request.user
    avatar_url = user.avatar.url if hasattr(user, 'avatar') and user.avatar else None
    initial = (user.first_name or user.username)[0].upper()
    is_teacher = course.is_teacher_of(user) or user.is_admin
 
    return JsonResponse({
        'id': comment.pk,
        'content': comment.content,
        'author_name': user.get_full_name() or user.username,
        'author_initial': initial,
        'avatar_url': avatar_url,
        'created_at': timesince(comment.created_at) + ' lalu',
        'is_own': True,
        'is_teacher': is_teacher,
        'parent_id': parent.pk if parent else None,
        'role_label': user.get_role_display() if hasattr(user, 'get_role_display') else '',
    })
 
 
@login_required
@require_POST
def comment_delete(request, comment_pk):
    comment = get_object_or_404(MaterialComment, pk=comment_pk)
    course = comment.material.module.course
 
    # Hanya penulis, guru, atau admin yang bisa hapus
    if not (comment.author == request.user or course.is_teacher_of(request.user) or request.user.is_admin):
        return JsonResponse({'error': 'Akses ditolak.'}, status=403)
 
    comment.is_deleted = True
    comment.content = '[Komentar telah dihapus]'
    comment.save()
    return JsonResponse({'success': True})
 