from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .models import Book


class IndexesTests(TestCase):

    def test_raises_error_without_field(self):
        msg = "Minimum one field is required to define an index."
        with self.assertRaisesMessage(ValueError, msg):
            models.Index(model=Book)

    def test_max_name_length(self):
        msg = "Index names cannot be longer than 30 chars."
        with self.assertRaisesMessage(ValidationError, msg):
            models.Index('title', name='looooooooooooong_index_name_idx')

    def test_name(self):
        index = models.Index('author', 'title', model=Book)
        self.assertEqual(index.name, 'model_index_author_de9d81_idx')

    def test_deconstruction(self):
        index = models.Index('title')
        path, args, kwargs = index.deconstruct()
        self.assertEqual(path, "django.db.models.Index")
        self.assertEqual(args, ('title',))
        self.assertEqual(kwargs, {})
