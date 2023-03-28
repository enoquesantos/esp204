import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

from tinymce.models import HTMLField



class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(
            is_deleted=True,
            deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None, is_deleted=False)

    def dead(self):
        return self.exclude(deleted_at=None, is_deleted=False)


class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = SoftDeletionQuerySet(self.model)
        return qs if not self.alive_only else qs.filter(is_deleted=False)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class AbstractModel(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False)
    obs = models.TextField(
        max_length=500,
        verbose_name="Observações",
        help_text="Observações de uso interno, não visível para os clientes.",
        null=True,
        blank=True)
    enabled = models.BooleanField(
        default=True,
        verbose_name="Habilitado",
        help_text="Items não habilitados não serão visíveis aos clientes no site.")
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Data do cadastro",
        help_text="Data e hora de quando o objeto foi registrado no sistema.")
    updated_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Última atualização",
        help_text="Data e hora da última atualização feita no objeto no sistema.")
    deleted_at = models.DateTimeField(
        blank=True,
        null=True)
    is_deleted = models.BooleanField(
        default=False,
        verbose_name="Deletado",
        help_text="Items marcados como deletado não serão visíveis no sistema.")
    created_by = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        verbose_name="Criado por",
        related_name='created_by_%(class)s_related'.lower(),
        null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False):
        """ soft delete a model instance """
        """ we never delete a object! Instead we mark he as deleted. """
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        super(AbstractModel, self).delete()

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
