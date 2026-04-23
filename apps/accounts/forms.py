from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import User, Jurusan

User = get_user_model()


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username atau Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if '@' in username:
            try:
                user_obj = User.objects.get(email__iexact=username)
                return user_obj.username
            except User.DoesNotExist:
                return username
        return username


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Depan'})
    )
    last_name = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Belakang'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    jurusan = forms.ModelChoiceField(
        queryset=Jurusan.objects.all(),
        empty_label='-- Pilih Jurusan --',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label='Jurusan'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Konfirmasi Password'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'jurusan', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'  # semua register otomatis jadi siswa
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'bio', 'phone', 'date_of_birth', 'avatar', 'jurusan')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-modern'}),
            'last_name': forms.TextInput(attrs={'class': 'input-modern'}),
            'email': forms.EmailInput(attrs={'class': 'input-modern'}),
            'bio': forms.Textarea(attrs={
                'class': 'textarea-modern', 
                'rows': 3, 
                'maxlength': '50',  # Pembatasi karakter
                'placeholder': 'Tulis bio singkat kamu...'
            }),
            'phone': forms.TextInput(attrs={'class': 'input-modern'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'input-modern', 'type': 'date'}),
            'avatar': forms.FileInput(attrs={'class': 'file-input', 'id': 'id_avatar'}),
            'jurusan': forms.Select(attrs={'class': 'input-modern'}),
        }

    def clean_bio(self):
        bio = self.cleaned_data.get('bio')
        if bio and len(bio) > 50:
            raise forms.ValidationError("Bio tidak boleh lebih dari 50 karakter.")
        return bio


class AdminUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'jurusan', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'jurusan': forms.Select(attrs={'class': 'form-select'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }