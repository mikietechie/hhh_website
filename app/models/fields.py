from django.db import models
from django.db.models.fields.files import ImageFieldFile, FieldFile


# FORM CONSTANTS
BLANK_OPTION = ("", "------")
BOTH_YES_NO_OPTIONS = [BLANK_OPTION, (True, "Yes"), (False, "No")]


#   Modified models fields
class FileImageField(ImageFieldFile):
    @property
    def url(self):
        return super().url if self.name else None


class FileField(FieldFile):
    @property
    def url(self):
        return super().url if self.name else None


class ImageField(models.ImageField):
    attr_class = FileImageField


class FileField(models.FileField):
    attr_class = FileField
