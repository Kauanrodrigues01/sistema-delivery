from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "phone", "cpf", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["full_name", "phone", "cpf", "user__username"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Informações do Usuário", {"fields": ("user",)}),
        (
            "Dados Pessoais",
            {"fields": ("full_name", "phone", "cpf", "address")},
        ),
        ("Status", {"fields": ("is_active",)}),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )
