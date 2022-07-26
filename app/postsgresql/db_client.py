import psycopg2

class DBClient:
    def __init__(self, db_connection:str):
        self.db = psycopg2.connect(db_connection)
        self.__schemas = {}
        self.__primary_key = {}

    def add_table_schema(self, table_name, schema: dict, primary_key: str):
        self.__schemas[table_name] = schema
        self.__primary_key[table_name] = primary_key

    def insert_single_data(self, data: dict, table):
        if not self.table_exists(table=table):
            self.create_table(table)
            
        query = f"""
        INSERT INTO {table} ({', '.join(data.keys())})
        VALUES ({', '.join([f"'{v}'" if type(v) == str else str(v) for v in data.values()])})
        """
        self.execute_query(query)
        self.db.commit()

    def execute_query(self, query):
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor

    def table_exists(self, table):
        query = f"""
        SELECT EXISTS (
            SELECT FROM
                information_schema.tables
            WHERE
                table_schema LIKE 'public' AND
                table_type LIKE 'BASE_TABLE' AND
                table_name = '{table}')
                """
        return self.execute_query(query).fetchone()[0]
        

    def create_table(self, table_name: str, schema=None):
        if schema == None:
            schema = self.__schemas[table_name]
        else:
            self.add_table_schema(table_name, schema)

        schema_unpacked = [" ".join(item) for item in schema.items()]

        query = f"CREATE TABLE {table_name} ({', '.join(schema_unpacked)}, PRIMARY KEY ({self.__primary_key[table_name]}))"
        self.execute_query(query)
        self.db.commit()


# if __name__ == "__main__":
#     data = {"test_key": "testvalues", "another_key": 58439085, "bool_key": True}
#     schema = {"test_key": "CHAR(255)", "another_key": "BIGINT", "bool_key": "BOOLEAN"}
#     client = DBClient("host=localhost dbname=postgres user=postgres password=postgres")
#     client.add_table_schema("test_table", schema)
#     client.insert_single_data(data, "test_table")