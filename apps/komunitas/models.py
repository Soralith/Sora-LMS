from django.db import models
from apps.accounts.models import User


class KomunitasMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='komunitas_messages')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='komunitas/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pesan Komunitas'
        verbose_name_plural = 'Pesan Komunitas'

    def __str__(self):
        return f"{self.user.username}: {self.content[:30] if self.content else 'Image'}"