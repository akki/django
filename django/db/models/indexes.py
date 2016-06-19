from __future__ import unicode_literals

import hashlib

from django.core.exceptions import ValidationError
from django.utils.encoding import force_bytes

__all__ = ['Index']

# The max length of the names of the indexes (restricted to 30 due to Oracle)
MAX_NAME_LENGTH = 30


class Index(object):

    index_type = 'idx'

    def __init__(self, *fields, **kwargs):
        if not fields:
            raise ValueError("Minimum one field is required to define an index.")
        self.fields = fields
        self._name = kwargs.get('name', '')
        if len(self._name) > MAX_NAME_LENGTH:
            raise ValidationError(
                "Index names cannot be longer than %s chars." % MAX_NAME_LENGTH
            )
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
        path = "%s.%s" % (self.__class__.__module__, self.__class__.__name__)
        path = path.replace("django.db.models.indexes", "django.db.models")
        return (path, self.fields, {})

    @staticmethod
    def _hash_generator(*args):
        """
        Generate a 32-bit digest of a set of arguments that can be used to
        shorten identifying names.
        """
        h = hashlib.md5()
        for arg in args:
            h.update(force_bytes(arg))
        return h.hexdigest()[:6]

    def get_name(self, suffix='_idx'):
        """
        Generate a unique name for the index.

        The name is divided into 3 parts - table name (12 chars), field name
        (8 chars) and unique hash + suffix (10 chars). Each part is made to
        fit its size by truncating the excess length.
        """
        table_name = self.model._meta.db_table
        column_names = self.fields
        hash_data = (table_name,) + column_names + (self.index_type,)
        index_unique_hash = self._hash_generator(*hash_data)
        table_part = table_name.replace('"', '').replace('.', '_')
        field_part = column_names[0].replace('"', '').replace('.', '_')
        hash_part = '%s%s' % (index_unique_hash, suffix)
        if len(table_part) > 11:
            table_part = table_part[:11]
        if len(field_part) > 7:
            field_part = field_part[:7]
        index_name = '%s_%s_%s' % (table_part, field_part, hash_part)
        # It shouldn't start with an underscore (Oracle hates this)
        if index_name[0] == "_":
            index_name = index_name[1:]
        # It can't start with a number on Oracle, so prepend D if we need to
        if index_name[0].isdigit():
            index_name = "D%s" % index_name[1:]
        return index_name

    def __repr__(self):
        return '<%s: fields="%s">' % (self.__class__.__name__, ', '.join(self.fields))

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.deconstruct() == other.deconstruct())

    def __ne__(self, other):
        return not (self == other)
