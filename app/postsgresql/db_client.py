import psycopg2

class DBClient:
    def __init__(self, db_connection:str):
        self.db = psycopg2.connect(db_connection)
        self.__schemas = {}
        self.__primary_key = {}
        self.__optimise_text_key = {}

    def add_table_schema(self, table_name, schema: dict, primary_key: str, optimise_text_keys=None or set):
        self.__schemas[table_name] = schema
        self.__primary_key[table_name] = primary_key
        self.__optimise_text_key[table_name] = optimise_text_keys

    def insert_single_data(self, data: dict, table_name: str):
        if not self.table_exists(table=table_name):
            self.create_table(table_name)

        optimise_keys = self.__optimise_text_key[table_name] ##################################
        if optimise_keys != None:
            for key in optimise_keys:
                opt_table_name = f"{table_name}_{key}"
                if not self.table_exists(opt_table_name):
                    schema = {"id": "SERIAL", key: "TEXT"}
                    self.add_table_schema(opt_table_name, schema, "id")
                    self.create_table(opt_table_name, schema)
                
                values = self.get_key_values_based_on_data(opt_table_name, "id", key, data[key])
                if len(values) == 0:
                    self.__insert_into(opt_table_name, [key], [data[key]])
                    values = self.get_key_values_based_on_data(opt_table_name, "id", key, data[key])
                
                data[key] = values[0][0]

        self.__insert_into(table_name, data.keys(), data.values())

    def __insert_into(self, table_name, keys, values):
        query = f"""
        INSERT INTO {table_name} ({', '.join(keys)})
        VALUES ({', '.join([f"'{v}'" if type(v) == str else str(v) for v in values])})
        """
        self.execute_query(query)
        self.db.commit()

    def execute_query(self, query):
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor

    def table_exists(self, table: str):
        query = f"""
        SELECT EXISTS (
            SELECT FROM
                information_schema.tables
            WHERE
                table_schema LIKE 'public' AND
                table_type LIKE 'BASE_TABLE' AND
                table_name = '{table}')
                """
        fetch = self.execute_query(query).fetchone()
        return fetch[0]

    def primary_key_exists(self, data_id: int, table: str, primary_key: str):
        query = f"""
            SELECT {primary_key} FROM {table} where id = {data_id}
        """
        cursor = self.execute_query(query)
        fetch = cursor.fetchone()
        try:
            if fetch != None:
                if fetch[0] == data_id:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(e)
            return False
        
    def get_key_values_based_on_data(self, table_name: str, target_key: str, from_key: str, value):
        query = f"""
            SELECT {target_key} FROM {table_name} WHERE {table_name}.{from_key} = {f"'{value}'" if type(value) == str else value}
        """
        cursor = self.execute_query(query)
        return cursor.fetchall()

    def create_table(self, table_name: str, schema=None):
        if schema == None:
            schema = self.__schemas[table_name]
        else:
            self.add_table_schema(table_name, schema, self.__primary_key[table_name])

        schema_unpacked = [" ".join(item) for item in schema.items()]

        query = f"CREATE TABLE {table_name} ({', '.join(schema_unpacked)}, PRIMARY KEY ({self.__primary_key[table_name]}))"
        self.execute_query(query)
        self.db.commit()
        print("Created table:", table_name)


# if __name__ == "__main__":
#     table_name = "test_fast_table"
#     data = {"id": 420691337, "another_key": 'yolo'}
#     schema = {"id": "SERIAL", "another_key": "TEXT"}

#     client = DBClient("host=localhost dbname=postgres user=postgres password=postgres")
#     client.add_table_schema(table_name, schema, "id")
#     data_exists = client.data_exists(420691337, table_name)
#     if not data_exists:
#         client.insert_single_data(data, table_name)
    
#     cursor

#     query = f"DROP TABLE {table_name}"
#     client.execute_query(query)