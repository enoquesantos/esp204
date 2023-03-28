from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# from .celerytasks import restart_services_on_setting_change


class Setting(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Nome da propriedade",
        help_text="O nome ou chave que identifica a informação.",
        unique=True)
    value = models.TextField(
        verbose_name="Valor",
        help_text="A informação referente a chave (name). O dado propriamente dito.",
        null=True,
        blank=True)
    enabled = models.BooleanField(
        verbose_name="Habilitado",
        help_text="Marque/Desmarque para habilitar essa variável no sistema.",
        default=True)
    obs = models.TextField(
        max_length=500,
        verbose_name="Observações",
        help_text="Observações de uso interno, não visível para os clientes.",
        null=True,
        blank=True)
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Data de criação")
    updated_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Data da última atualização")

    class Meta:
        db_table = 'config_settings'
        verbose_name = 'Configurações Internas'
        verbose_name_plural = 'Configurações Internas'

    def __str__(self):
        return "%s - %s" % (str(self.name), self.created_at.strftime("%d/%m/%Y %H:%M:%S"))

    def save(self, *args, **kwargs):
        super(Setting, self).save(*args, **kwargs)
        # restart_services_on_setting_change.apply_async(kwargs={}, countdown=1)
