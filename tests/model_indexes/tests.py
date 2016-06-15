from django.db import models
from django.test import TestCase

from .models import Book


class IndexesTests(TestCase):

    def test_raises_error_without_field(self):
        msg = "Minimum one field is required to define an index."
        with self.assertRaisesMessage(ValueError, msg):
            models.Index(model=Book)

    def test_name(self):
        index = models.Index('title', 'author', model=Book)
        self.assertEqual(index.name, 'model_index_title_7be80f0d_idx')
