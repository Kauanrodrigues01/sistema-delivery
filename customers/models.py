from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    """
    Modelo de Cliente Fiel

    Clientes fiéis são usuários cadastrados pelo administrador que podem
    fazer login para ter seus dados preenchidos automaticamente no checkout.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        help_text="Usuário vinculado (não é superuser)",
    )
    full_name = models.CharField(max_length=200, verbose_name="Nome Completo")
    phone = models.CharField(max_length=20, db_index=True, verbose_name="Telefone")
    cpf = models.CharField(
        max_length=14,
        unique=True,
        blank=True,
        null=True,
        verbose_name="CPF",
        help_text="CPF do cliente (opcional, mas recomendado)",
    )
    address = models.TextField(verbose_name="Endereço Principal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Ativo", db_index=True)

    class Meta:
        verbose_name = "Cliente Fiel"
        verbose_name_plural = "Clientes Fiéis"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["cpf"]),
            models.Index(fields=["is_active", "created_at"]),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.phone}"
