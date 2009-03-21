from django.db.backends.creation import BaseDatabaseCreation
from utils import *


__all__ = ('DatabaseCreation',)


class DatabaseCreation(BaseDatabaseCreation):
    """
    @summary: Django CouchDB backend's implementation for Django's
    BaseDatabaseCreation class.
    """
    class DummyDataTypes:
        def __getitem__(self, key): return "type"

    data_types = DummyDataTypes()


    def sql_create_model(self, model, style, seen_models=set()):
        data, pending_references = {}, {}

        opts = model._meta


        # Browsing through fields to find references
        for field in opts.local_fields:
            col_type = field.db_type()

            if col_type is None:
                continue

            options = {}

            if not field.null:
                options['NOT NULL'] = True
            if field.primary_key:
                options['PRIMARY KEY'] = True
            if field.unique:
                options['UNIQUE'] = True

            if field.rel:
                ref_fake_sql, pending = \
                    self.sql_for_inline_foreign_key_references(field,
                                                               seen_models,
                                                               style)

                if pending:
                    pr = pending_references.setdefault(field.rel.to, []).\
                                            append((model, field))

            data.update({field.column: options})

        # Makes fake SQL
        fake_output = [SQL('create', (opts.db_table, data) )]

        return fake_output, pending_references

    def sql_for_inline_foreign_key_references(self, field, known_models, style):
        pending = field.rel.to in known_models
        return [], pending

    def sql_for_many_to_many_field(self, model, field, style):
        return []
        """
        """


    def sql_for_pending_references(self, model, style, pending_references):
        fake_output = []
        opts = model._meta
        if model in pending_references:
            for rel_class, f in pending_references[model]:
                rel_opts = rel_class._meta
                r_table = rel_opts.db_table
                r_col = f.column
                table = opts.db_table
                #~ col = opts.get_field(f.rel.field_name).column
                fake_output.append(SQL('add_foreign_key', (r_table, r_col, table)))
            del pending_references[model]
        return fake_output
