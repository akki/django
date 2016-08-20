import unittest

from django.db import connection
from django.db.backends.signals import connection_created
from django.test import TestCase


@unittest.skipUnless(connection.vendor == 'postgresql', "PostgreSQL specific tests")
class PostgreSQLTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        # No need to keep that signal overhead for non PostgreSQL-related tests.
        from django.contrib.postgres.signals import register_hstore_handler

        connection_created.disconnect(register_hstore_handler)
        super(PostgreSQLTestCase, cls).tearDownClass()

    def get_indexed_columns(self, table):
        """
        Get the single-column indexes on the table using a new cursor.
        """
        with connection.cursor() as cursor:
            return [
                c['columns'][0]
                for c in connection.introspection.get_constraints(cursor, table).values()
                if c['index'] and len(c['columns']) == 1
            ]
