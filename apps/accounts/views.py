from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .forms import LoginForm, RegisterForm, ProfileUpdateForm, AdminUserCreateForm
from .models import User
from apps.courses.models import Enrollment, Course


def auth_status(request):
    """Simple API endpoint to check if user is authenticated."""
    if request.user.is_authenticated:
        avatar_url = None
        if request.user.avatar:
            avatar_url = request.build_absolute_uri(request.user.avatar.url)
        
        return JsonResponse({
            'is_authenticated': True,
            'username': request.user.username,
            'name': request.user.get_full_name() or request.user.username,
            'role': request.user.role,
            'avatar_url': avatar_url,
        })
    return JsonResponse({'is_authenticated': False})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah.')

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Akun berhasil dibuat!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Periksa kembali data yang dimasukkan.')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Anda telah keluar.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user_profile': request.user})


@login_required
def profile_edit(request):
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('accounts:profile')

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def user_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Akses ditolak.')
        return redirect('dashboard:index')

    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    if role_filter:
        users = users.filter(role=role_filter)

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'query': query,
        'role_filter': role_filter,
    })


@login_required
def user_create(request):
    if not request.user.is_admin:
        messages.error(request, 'Akses ditolak.')
        return redirect('dashboard:index')

    form = AdminUserCreateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Pengguna berhasil ditambahkan!')
            return redirect('accounts:user_list')

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Tambah'})


@login_required
def user_edit(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Akses ditolak.')
        return redirect('dashboard:index')

    user = get_object_or_404(User, pk=pk)
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Data pengguna berhasil diperbarui!')
            return redirect('accounts:user_list')

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Edit', 'target_user': user})


@login_required
def user_delete(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Akses ditolak.')
        return redirect('dashboard:index')

    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Pengguna berhasil dihapus.')
        return redirect('accounts:user_list')

    return render(request, 'accounts/user_confirm_delete.html', {'target_user': user})

@login_required
def user_detail_ajax(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail_modal.html', {'u': target_user})