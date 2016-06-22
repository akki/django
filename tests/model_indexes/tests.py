from django.db import models
from django.test import TestCase

from .models import Book


class IndexesTests(TestCase):

    def test_raises_error_without_field(self):
        msg = 'At least one field is required to define an index.'
        with self.assertRaisesMessage(ValueError, msg):
            models.Index()

    def test_max_name_length(self):
        # When user provides index name longer than 30 characters
        msg = 'Index names cannot be longer than 30 characters.'
        with self.assertRaisesMessage(ValueError, msg):
            models.Index(fields=['title'], name='looooooooooooong_index_name_idx')

        # To check if auto-generated name is not more than 30 characters
        index = models.Index(fields=['title'])
        index.model = Book
        self.assertTrue(len(index.name) <= 30)

    def test_name_constraints(self):
        msg = 'Index names cannot start with an underscore (_).'
        with self.assertRaisesMessage(ValueError, msg):
            models.Index(fields=['title'], name='_name_starting_with_underscore')

        msg = 'Index names cannot start with a number (0-9).'
        with self.assertRaisesMessage(ValueError, msg):
            models.Index(fields=['title'], name='5name_starting_with_number')

    def test_name_auto_generation(self):
        index = models.Index(fields=['author', 'title'])
        index.model = Book
        self.assertEqual(index.name, 'model_index_author_de9d81_idx')

    def test_deconstruction(self):
        index = models.Index(fields=['title'])
        path, args, kwargs = index.deconstruct()
        self.assertEqual(path, 'django.db.models.Index')
        self.assertEqual(args, ())
        self.assertEqual(kwargs, {'fields': ['title']})
