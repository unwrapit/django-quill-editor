import json
import warnings

from django.db import models
from django.utils.html import strip_tags

from .forms import QuillFormJSONField
from .quill import Quill, QuillParseError

__all__ = (
    'FieldQuill',
    'QuillDescriptor',
    'QuillField',
    'QuillTextField',
    'QuillJSONField'
)


class FieldQuill:
    def __init__(self, instance, field, json_string):
        self.instance = instance
        self.field = field
        self.json_string = json_string or '{"delta":"","html":""}'
        self._committed = True

    def __str__(self):
        return self.delta
        
    def __eq__(self, other):
        if hasattr(other, "json_string"):
            return self.json_string == other.json_string
        return self.json_string == other

    def __hash__(self):
        return hash(self.json_string)

    def _require_quill(self):
        if not self:
            raise ValueError(
                "The '%s' attribute has no Quill JSON String associated with it."
                % self.field.name
            )

    def _get_quill(self):
        self._require_quill()
        self._quill = Quill(self.json_string)
        return self._quill

    def _set_quill(self, quill):
        self._quill = quill

    def _del_quill(self):
        del self._quill

    quill = property(_get_quill, _set_quill, _del_quill)

    @property
    def html(self):
        self._require_quill()
        return self.quill.html

    @property
    def delta(self):
        self._require_quill()
        return self.quill.delta

    @property
    def plain(self):
        self._require_quill()
        return self.quill.plain

    def save(self, json_string, save=True):
        setattr(self.instance, self.field.name, json_string)
        self._committed = True
        if save:
            self.instance.save()


class QuillDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        if self.field.name in instance.__dict__:
            quill = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            quill = getattr(instance, self.field.name)

        if isinstance(quill, str) or quill is None:
            attr = self.field.attr_class(instance, self.field, quill)
            instance.__dict__[self.field.name] = attr

        elif isinstance(quill, Quill) and not isinstance(quill, FieldQuill):
            quill_copy = self.field.attr_class(instance, self.field, quill.json_string)
            quill_copy.quill = quill
            instance.__dict__[self.field.name] = quill_copy

        elif isinstance(quill, FieldQuill) and not hasattr(quill, "field"):
            quill.instance = instance
            quill.field = self.field

        elif isinstance(quill, FieldQuill) and instance is not quill.instance:
            quill.instance = instance

        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value


class QuillFieldMixin:
    attr_class = FieldQuill
    descriptor_class = QuillDescriptor

    def formfield(self, **kwargs):
        kwargs.update({'form_class': self._get_form_class()})
        return super().formfield(**kwargs)

    @staticmethod
    def _get_form_class():
        return QuillFormJSONField

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        """
        Expect a JSON string with 'delta' and 'html' keys
        ex) b'{"delta": "...", "html": "..."}'
        :param value: JSON string with 'delta' and 'html' keys
        :return: Quill's 'Delta' JSON String
        """
        print("to_python", type(value))
        if value is None:
            return value
        if isinstance(value, Quill):
            return value
        if isinstance(value, FieldQuill):
            return value.quill
        if isinstance(value, str):
            return Quill(value)
        if isinstance(value, dict):
            return Quill(json.loads(value))
        return None

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        if isinstance(value, (Quill, FieldQuill)):
            return value.json_string
        return value

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class QuillTextField(QuillFieldMixin, models.TextField):
    pass


def QuillField(*args, **kwargs):
    warnings.warn('QuillField is deprecated in favor of QuillTextField', stacklevel=2)
    return QuillTextField(*args, **kwargs)


class QuillJSONField(QuillFieldMixin, models.JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, str):
            value = json.loads(value)
        return self.to_python(value)

    def validate(self, value, model_instance):
        value = self.get_prep_value(value)
        super(QuillJSONField, self).validate(value, model_instance)
