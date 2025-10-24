from decouple import config
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

SUPERUSER_USERNAME = config("SUPERUSER_USERNAME", default="admin", cast=str)
SUPERUSER_EMAIL = config("SUPERUSER_EMAIL", default="admin@gmail.com", cast=str)
SUPERUSER_PASSWORD = config("SUPERUSER_PASSWORD", default="admin", cast=str)


@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    """
    Cria automaticamente um usuário admin após as migrações.
    Executa apenas uma vez, não recria se já existir.
    """
    # Só executa para o app 'core' para evitar execuções duplicadas
    if sender.name == "core":
        user, created = User.objects.get_or_create(
            username=SUPERUSER_USERNAME,
            defaults={
                "email": SUPERUSER_EMAIL,
                "is_superuser": True,
                "is_staff": True,
            },
        )

        if created:
            user.set_password(SUPERUSER_PASSWORD)
            user.save()
            print(f"✅ Superuser '{SUPERUSER_USERNAME}' created successfully")
        else:
            print(f"ℹ️  Superuser '{SUPERUSER_USERNAME}' already exists")
