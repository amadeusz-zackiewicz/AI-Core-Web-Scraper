import pandas as PD
import sqlalchemy as SA

class DataCleaner:
    def __init__(self):
        self._columns_clean_ups = {}
        self._column_types = {}

    def add_column_constraint(self, key: str, target_type: str, clean_up_funcs):
        self._columns_clean_ups[key] = clean_up_funcs
        self._column_types = target_type

    def remove_column_constraint(self, key: str):
        if key in self._columns_clean_ups:
            del self._columns_clean_ups[key]
        if key in self._column_types:
            del self._column_types[key]

    def clean_up_value(self, key: str, value):
        if key in self._columns_clean_ups:
            if type(self._columns_clean_ups[key]) == list:
                for func in self._columns_clean_ups:
                    value = func(value, self._column_types[key])
            else:
                return self._columns_clean_ups(value, self._column_types[key])
        else:
            return value

    def clean_up_entry(self, row: dict):
        for key, value in row:
            row[key] = self.clean_up_value(key, value)

    #def clean_up_data(self, data: SA.table):
