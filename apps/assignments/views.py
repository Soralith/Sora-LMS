from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.courses.models import Course, Enrollment
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeForm


@login_required
def tugas_saya(request):
    if not request.user.is_student:
        return redirect('courses:course_list')
    
    enrollments = Enrollment.objects.filter(student=request.user, is_active=True).select_related('course')
    course_ids = enrollments.values_list('course_id', flat=True)
    
    assignments = Assignment.objects.filter(
        course_id__in=course_ids,
        is_published=True
    ).select_related('course').order_by('-due_date')
    
    submission_map = {}
    for sub in Submission.objects.filter(student=request.user, assignment__in=assignments):
        submission_map[sub.assignment_id] = sub
    
    pending_assignments = []
    submitted_assignments = []
    graded_assignments = []
    
    for assignment in assignments:
        sub = submission_map.get(assignment.id)
        item = {
            'assignment': assignment,
            'submission': sub,
            'due_date': assignment.due_date,
            'is_overdue': assignment.is_overdue(),
        }
        
        if sub:
            if sub.status in ('graded', 'returned'):
                graded_assignments.append(item)
            else:
                submitted_assignments.append(item)
        elif assignment.is_overdue():
            pending_assignments.append(item)
        else:
            pending_assignments.append(item)
    
    return render(request, 'assignments/tugas_saya.html', {
        'pending_assignments': pending_assignments,
        'submitted_assignments': submitted_assignments,
        'graded_assignments': graded_assignments,
    })


@login_required
def assignment_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    if request.user.is_student:
        get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)

    assignments = course.assignments.filter(is_published=True) if request.user.is_student \
        else course.assignments.all()

    submission_map = {}
    if request.user.is_student:
        for sub in Submission.objects.filter(student=request.user, assignment__course=course):
            submission_map[sub.assignment_id] = sub

    return render(request, 'assignments/assignment_list.html', {
        'course': course,
        'assignments': assignments,
        'submission_map': submission_map,
    })


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    course = assignment.course
    submission = None

    if request.user.is_student:
        get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)
        submission = Submission.objects.filter(student=request.user, assignment=assignment).first()

    submissions = None
    if request.user.is_teacher or request.user.is_admin:
        submissions = assignment.submissions.select_related('student').all()

    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'course': course,
        'submission': submission,
        'submissions': submissions,
    })


@login_required
def assignment_create(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_detail', slug=course_slug)

    form = AssignmentForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.course = course
        assignment.save()
        messages.success(request, 'Tugas berhasil ditambahkan!')
        return redirect('assignments:assignment_detail', pk=assignment.pk)

    return render(request, 'assignments/assignment_form.html', {
        'form': form, 'course': course, 'action': 'Buat'
    })


@login_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    course = assignment.course
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = AssignmentForm(request.POST or None, request.FILES or None, instance=assignment)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tugas berhasil diperbarui!')
        return redirect('assignments:assignment_detail', pk=pk)

    return render(request, 'assignments/assignment_form.html', {
        'form': form, 'course': course, 'assignment': assignment, 'action': 'Edit'
    })


@login_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    course = assignment.course
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Tugas berhasil dihapus.')
        return redirect('courses:course_detail', slug=course.slug)

    return render(request, 'assignments/assignment_confirm_delete.html', {
        'assignment': assignment, 'course': course
    })


@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, is_published=True)
    course = assignment.course
    get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)

    if Submission.objects.filter(student=request.user, assignment=assignment).exists():
        messages.info(request, 'Anda sudah mengumpulkan tugas ini.')
        return redirect('assignments:assignment_detail', pk=pk)

    form = SubmissionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        submission = form.save(commit=False)
        submission.assignment = assignment
        submission.student = request.user
        if assignment.is_overdue():
            submission.status = 'late'
        submission.save()
        messages.success(request, 'Tugas berhasil dikumpulkan!')
        return redirect('assignments:assignment_detail', pk=pk)

    return render(request, 'assignments/submit_assignment.html', {
        'form': form, 'assignment': assignment, 'course': course
    })


@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    course = submission.assignment.course
    if not (request.user == course.teacher or request.user.is_admin):
        messages.error(request, 'Akses ditolak.')
        return redirect('courses:course_list')

    form = GradeForm(request.POST or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        sub = form.save(commit=False)
        sub.status = 'graded'
        sub.graded_at = timezone.now()
        sub.graded_by = request.user
        sub.save()
        messages.success(request, f'Nilai untuk {submission.student.username} berhasil disimpan!')
        return redirect('assignments:assignment_detail', pk=submission.assignment.pk)

    return render(request, 'assignments/grade_submission.html', {
        'form': form, 'submission': submission, 'course': course
    })
