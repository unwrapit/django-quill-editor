import json

__all__ = (
    "QuillParseError",
    "Quill",
)

from django.utils.html import strip_tags


class QuillParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Failed to parse value(%s)" % self.value


class Quill:
    def __init__(self, data):
        assert isinstance(data, dict), (
            "Quill expects dictionary as data but got %s(%s)." % (type(data), data)
        )
        self.data = data
        try:
            self.delta = data['delta']
            self.html = data['html']
        except (KeyError, TypeError):
            raise QuillParseError(data)
