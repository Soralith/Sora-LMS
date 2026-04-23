from django.db import models


class AISettings(models.Model):
    name = models.CharField(
        max_length=100, 
        default='Default',
        verbose_name='Nama Pengaturan'
    )
    gemini_api_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Kunci API Gemini',
        help_text='API key untuk Gemini'
    )
    system_instruction = models.TextField(
        default='Kamu adalah asisten AI di Sora LMS, sebuah platform pembelajaran online. Bantu siswa, guru, dan admin dengan pertanyaan seputar pembelajaran, materi pelajaran, dan penggunaan platform. Jawab dalam Bahasa Indonesia yang ramah dan jelas.',
        verbose_name='Instruksi Sistem',
        help_text='Instruksi sistem untuk AI (hidden prompt)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Aktif'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Dibuat'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Diperbarui'
    )

    class Meta:
        verbose_name = 'Pengaturan AI'
        verbose_name_plural = 'Pengaturan AI'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            AISettings.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_settings(cls):
        return cls.objects.filter(is_active=True).first()