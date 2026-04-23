from django.db import migrations

def create_jurusan(apps, schema_editor):
    Jurusan = apps.get_model('accounts', 'Jurusan')
    data = [
        ('RPL', 'Rekayasa Perangkat Lunak'),
        ('AKL', 'Akuntansi Keuangan Lembaga'),
        ('PMN', 'Pemasaran'),
        ('TKJ', 'Teknik Komputer Jaringan'),
        ('DKV', 'Desain Komunikasi Visual'),
    ]
    for kode, nama in data:
        # Gunakan field yang sesuai dengan models.py Jurusan kamu
        Jurusan.objects.get_or_create(nama=nama) 

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_jurusan_alter_user_role_user_jurusan'), # Sesuaikan nama file 0002 kamu
    ]

    operations = [
        migrations.RunPython(create_jurusan),
    ]