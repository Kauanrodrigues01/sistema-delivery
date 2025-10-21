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
    
    @property
    def formated_cpf(self):
        """Retorna o CPF formatado como XXX.XXX.XXX-XX ou vazio se não houver CPF."""
        if not self.cpf:
            return ""
        cpf_numbers = ''.join(filter(str.isdigit, self.cpf))
        if len(cpf_numbers) != 11:
            return self.cpf  # Retorna como está se não tiver 11 dígitos
        return f"{cpf_numbers[:3]}.{cpf_numbers[3:6]}.{cpf_numbers[6:9]}-{cpf_numbers[9:]}"
    
    @property
    def formated_phone(self):
        """Retorna o telefone formatado no padrão (XX) XXXXX-XXXX ou vazio se não houver telefone."""
        if not self.phone:
            return ""
        phone_numbers = ''.join(filter(str.isdigit, self.phone))
        if len(phone_numbers) == 10:
            return f"({phone_numbers[:2]}) {phone_numbers[2:6]}-{phone_numbers[6:]}"
        elif len(phone_numbers) == 11:
            return f"({phone_numbers[:2]}) {phone_numbers[2:7]}-{phone_numbers[7:]}"
        return self.phone  # Retorna como está se não tiver 10 ou 11 dígitos
