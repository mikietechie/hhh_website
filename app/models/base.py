from __future__ import annotations
import typing

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class Base(models.Model):
    class Meta:
        abstract = True
    
    str_prefix: str
    creation_date = models.DateField(auto_now_add=True)
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    edit_date = models.DateField(auto_now=True)
    edit_timestamp = models.DateTimeField(auto_now=True)
    created_by: models.ForeignKey[typing.Union[AbstractUser, Base]] = (
    )
    updated_by: models.ForeignKey[typing.Union[AbstractUser, Base]] = (
        models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.SET_NULL,
            blank=True,
            null=True,
            related_name="updated_%(app_label)s_%(class)ss",
        )
    )
    
    @property
    def sys_name(self):
        return str(self)

    @property
    def sm_str(self):
        return f"{self.str_prefix}-{self.str_id}"

    @property
    def str_id(self):
        return str(self.pk).rjust(8, "0")

    @classmethod
    def iter_as_choices(cls, *args):
        return tuple([(i, i) for i in args])
    
    def after_save(self, is_creation: bool):
        pass
