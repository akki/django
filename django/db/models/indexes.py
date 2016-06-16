from __future__ import unicode_literals

import hashlib

from django.utils.encoding import force_bytes

__all__ = ['Index']

# Max length restriction on names imposed by Oracle
MAX_NAME_LENGTH = 30


class Index(object):

    index_type = 'idx'

    def __init__(self, *fields, **kwargs):
        if not fields:
            raise ValueError("Minimum one field is required to define an index.")
        self.fields = fields
        self._name = kwargs.get('name')
        if 'model' in kwargs:
            self.model = kwargs['model']

    @property
    def name(self):
        if not self._name:
            self._name = self.get_name()
        return self._name

    def create_sql(self, schema_editor, suffix=''):
        columns = [field for field in self.fields]
        fields = [self.model._meta.get_field(field) for field in self.fields]
        if len(fields) == 1 and fields[0].db_tablespace:
            tablespace_sql = schema_editor.connection.ops.tablespace_sql(fields[0].db_tablespace)
        elif self.model._meta.db_tablespace:
            tablespace_sql = schema_editor.connection.ops.tablespace_sql(self.model._meta.db_tablespace)
        else:
            tablespace_sql = ""
        if tablespace_sql:
            tablespace_sql = " " + tablespace_sql

        quote_name = schema_editor.quote_name
        return schema_editor.sql_create_index % {
            "table": quote_name(self.model._meta.db_table),
            "name": quote_name(self.name),
            "columns": ", ".join(quote_name(column) for column in columns),
            "extra": tablespace_sql,
        }

    def remove_sql(self, schema_editor):
        quote_name = schema_editor.quote_name
        return schema_editor.sql_delete_index % {
            "table": quote_name(self.model._meta.db_table),
            "name": quote_name(self.name),
        }

    def deconstruct(self):
        """
        Returns a 3-tuple of class import path, positional arguments, and keyword
        arguments.
        """
        return (self.__class__.__name__, self.fields, {})

    def __repr__(self):
        return '<%s: fields="%s">' % (self.__class__.__name__, ', '.join(self.fields))

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.deconstruct() == other.deconstruct())

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def _hash_generator(*args):
        """
        Generate a 32-bit digest of a set of arguments that can be used to
        shorten identifying names.
        """
        h = hashlib.md5()
        for arg in args:
            h.update(force_bytes(arg))
        return h.hexdigest()[:8]

    def get_name(self, suffix=None):
        """
        Generate a unique name for the index.
        """
        if suffix is None:
            suffix = '_%s' % self.index_type
        column_names = self.fields
        # If there is just one column in the index, use a default algorithm from Django
        table_name = self.model._meta.db_table
        index_unique_hash = self._hash_generator(column_names)
        index_name = ('%s_%s_%s%s' % (
            table_name, column_names[0], index_unique_hash, suffix
        )).replace('"', '').replace('.', '_')
        # If the name is too long chop off characters from the prefix_part of the name
        if len(index_name) > MAX_NAME_LENGTH:
            # If table name is too long keep it in the prefix_part
            prefix_part = table_name
            suffix_part = ('_%s_%s%s' % (column_names[0], index_unique_hash, suffix))
            if len(suffix_part) > MAX_NAME_LENGTH:  # When column_names[0] is too long
                # If column name is too long keep it in the prefix_part
                prefix_part = ('%s_%s' % (table_name, column_names[0]))
                suffix_part = ('_%s%s' % (index_unique_hash, suffix))
            index_name = '%s%s' % (
                prefix_part[:(MAX_NAME_LENGTH - len(suffix_part))], suffix_part
            )
        # It shouldn't start with an underscore (Oracle hates this)
        if index_name[0] == "_":
            index_name = index_name[1:]
        # It can't start with a number on Oracle, so prepend D if we need to
        if index_name[0].isdigit():
            index_name = "D%s" % index_name[1:]
        return index_name
