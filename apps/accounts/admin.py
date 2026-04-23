from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Jurusan # Tambahkan import Jurusan

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. Tambahkan 'jurusan' di daftar tabel (list_display)
    list_display = ('username', 'email', 'role', 'jurusan', 'is_active', 'date_joined')
    
    # 2. Tambahkan 'jurusan' di filter samping
    list_filter = ('role', 'jurusan', 'is_active', 'is_staff')
    
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # 3. Tambahkan 'jurusan' di halaman EDIT user
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi Tambahan', {
            'fields': ('role', 'jurusan', 'avatar', 'bio', 'phone', 'date_of_birth')
        }),
    )

    # 4. Tambahkan 'jurusan' di halaman TAMBAH user baru
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informasi Tambahan', {
            'fields': ('role', 'jurusan', 'email', 'first_name', 'last_name')
        }),
    )

# 5. Daftarkan model Jurusan agar bisa dikelola datanya
@admin.register(Jurusan)
class JurusanAdmin(admin.ModelAdmin):
    list_display = ('nama', 'kode') # Sesuaikan dengan field di model Jurusan kamu