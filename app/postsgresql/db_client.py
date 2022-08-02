import psycopg2

class DBClient:
    """
    This client can be used to abstract connecting to and running quaries on a PostgreSQL database.
    """
    def __init__(self, db_connection:str):
        """
        Connect the client to a database.

        Args:
            db_connection: Arguments that will be used to connect to the database as a single string, 
            please check psycopg2 docs for details.
        """
        self.db = psycopg2.connect(db_connection)
        self.__schemas = {}
        self.__primary_key = {}
        self.__optimise_text_key = {}

    def add_table_schema(self, table_name, schema: dict, primary_key: str, optimise_text_keys=None or set):
        """
        Add information on how specific table rows should be handled.

        Args:
            table_name: name of the table that this schema governs
            schema: the schema that will be used to govern the table
            primary_key: the name of the primary key that is used to retrieve and sort data
            optimise_text_keys: a new table will be created for each key that will contain ID - TEXT pair, the original value of the
            key will be substituted with ID pointing to the TEXT. This can reduce the amount of storage space used for storing text
            data that is expected to repeat, such make of car.
        """
        self.__schemas[table_name] = schema
        self.__primary_key[table_name] = primary_key
        self.__optimise_text_key[table_name] = optimise_text_keys

    def insert_single_row(self, data: dict, table_name: str):
        """
        Insert a single row into the table, a schema will be used automatically.

        Args:
            data: a dictionary mapping key : values
            table_name: which table should the data be inserted into
        
        """
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

    def execute_query(self, query: str):
        """
        Execute the query on the database.

        Args:
            query: the query to be executed

        Returns:
            Cursor that points to the queried data
        """
        cursor = self.db.cursor()
        cursor.execute(query)
        return cursor

    def table_exists(self, table: str):
        """
        Check if a table with the given name already exists.

        Args:
            table: name of the table

        Returns:
            bool
        """
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

    def primary_key_exists(self, value: int, table: str, primary_key=None or str):
        """
        Check if the specified value of primary key already exists. Can be used to prevent duplicate data being collected.

        Args:
            value: the value to check
            table: the name of the table used to check
            primary_key: primary key used to in checking, if none specified one will be retrieved from schema

        Returns:
            bool
        """

        if primary_key == None:
            primary_key = self.__primary_key[table]

        query = f"""
            SELECT {primary_key} FROM {table} where id = {value}
        """
        cursor = self.execute_query(query)
        fetch = cursor.fetchone()
        try:
            if fetch != None:
                if fetch[0] == value:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            print(e)
            return False
        
    def get_key_values_based_on_data(self, table_name: str, target_key: str, from_key: str, value):
        """
        Get value of key based on a value of another key.

        Args:
            table_name: name of the table to execute query on
            target_key: the key to retrieve value from
            from_key: the key which will be used to compare values
            value: the value to compare to

        Returns:
            A list of matching values
        """
        query = f"""
            SELECT {target_key} FROM {table_name} WHERE {table_name}.{from_key} = {f"'{value}'" if type(value) == str else value}
        """
        cursor = self.execute_query(query)
        return cursor.fetchall()

    def create_table(self, table_name: str, schema=None, primary_key=None, optimise=None):
        """
        Create a table.

        Args:
            table_name: name of the table
            schema: the schema that will govern this table
            primary_key: primary key of this table
            optimise: a new table will be created for each key that will contain ID - TEXT pair, the original value of the
            key will be substituted with ID pointing to the TEXT. This can reduce the amount of storage space used for storing text
            data that is expected to repeat, such make of car.
        
        """
        if schema == None:
            schema = self.__schemas[table_name]
        if primary_key == None:
            try:
                primary_key = self.__primary_key[table_name]
            except:
                pass
        if optimise == None:
            try:
                optimise = self.__optimise_text_key[table_name]
            except:
                pass

        self.add_table_schema(table_name, schema, primary_key, optimise)

        schema_unpacked = [" ".join(item) for item in schema.items()]

        query = f"CREATE TABLE {table_name} ({', '.join(schema_unpacked)}, PRIMARY KEY ({primary_key}))"
        self.execute_query(query)
        self.db.commit()
        print("Created table:", table_name)

    def close(self):
        pass