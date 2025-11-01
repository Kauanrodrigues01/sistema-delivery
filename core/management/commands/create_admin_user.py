from decouple import config
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

SUPERUSER_USERNAME = config("SUPERUSER_USERNAME", default="admin", cast=str)
SUPERUSER_EMAIL = config("SUPERUSER_EMAIL", default="admin@gmail.com", cast=str)
SUPERUSER_PASSWORD = config("SUPERUSER_PASSWORD", default="admin", cast=str)


class Command(BaseCommand):
    help = "Create superusers from environment variables (supports multiple users separated by comma)"

    def handle(self, *args, **kwargs):
        # Dividir as variáveis de ambiente por vírgula
        usernames = [u.strip() for u in SUPERUSER_USERNAME.split(",")]
        emails = [e.strip() for e in SUPERUSER_EMAIL.split(",")]
        passwords = [p.strip() for p in SUPERUSER_PASSWORD.split(",")]

        # Verificar se todas as listas têm o mesmo tamanho
        if not (len(usernames) == len(emails) == len(passwords)):
            self.stdout.write(
                self.style.ERROR(
                    "Erro: As variáveis SUPERUSER_USERNAME, SUPERUSER_EMAIL e SUPERUSER_PASSWORD "
                    "devem ter a mesma quantidade de valores separados por vírgula"
                )
            )
            return

        # Criar cada usuário
        for username, email, password in zip(usernames, emails, passwords, strict=True):
            # Pular se algum campo estiver vazio
            if not username or not password:
                self.stdout.write(
                    self.style.WARNING(
                        f"Pulando usuário com dados incompletos: username='{username}'"
                    )
                )
                continue

            # Se o email for 'none', usar string vazia
            if email.lower() == "none":
                email = ""

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "is_superuser": True,
                    "is_staff": True,
                },
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Superuser '{username}' created successfully")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Superuser '{username}' already exists")
                )
