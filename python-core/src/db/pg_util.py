import asyncio
import logging
import os

import psycopg_pool

# This class is used to access an Azure PostgreSQL account
# via the psycopg library and asynchronous SDK methods.
# Chris Joakim, 3Cloud


class PGUtil:

    pool = None

    @classmethod
    async def initialze_pool(cls) -> psycopg_pool.AsyncConnectionPool:
        """
        Create and open a psycopg_pool.AsyncConnectionPool
        which is used throughout this module.
        """
        if PGUtil.pool is not None:
            logging.info("PGUtil#initialze_pool already exists...")
            return PGUtil.pool

        conn_pool_max_size = 1
        logging.info("PGUtil#initialze_pool creating new...")
        conn_str = cls.pg_connection_str()
        conn_str_tokens = conn_str.split("password")
        logging.info(
            "PGUtil#initialze_pool, conn_str: {} password=<omitted>".format(
                conn_str_tokens[0]
            )
        )
        PGUtil.pool = psycopg_pool.AsyncConnectionPool(
            conninfo=conn_str, open=False, min_size=1, max_size=conn_pool_max_size
        )
        logging.info(
            "PGUtil#initialze_pool, pool created: {}".format(PGUtil.pool)
        )
        await PGUtil.pool.open()
        await PGUtil.pool.check()
        logging.info("PGUtil#initialze_pool, pool opened")
        return PGUtil.pool

    @classmethod
    def envvar(cls, name: str, default: str = "") -> str:
        """
        Return the value of the given environment variable name,
        or the given default value."""
        if name in os.environ:
            return os.environ[name].strip()
        return default
    
    @classmethod
    def postgresql_server(cls) -> str:
        return cls.envvar("AZURE_PG_FLEX_SERVER", None)

    @classmethod
    def postgresql_port(cls) -> str:
        return cls.envvar("AZURE_PG_FLEX_PORT", "5432")

    @classmethod
    def postgresql_database(cls) -> str:
        return cls.envvar("AZURE_PG_FLEX_DB", None)

    @classmethod
    def postgresql_user(cls) -> str:
        return cls.envvar("AZURE_PG_FLEX_USER", None)

    @classmethod
    def postgresql_password(cls) -> str:
        return cls.envvar("AZURE_PG_FLEX_PASS", None)

    @classmethod
    def pg_connection_str(cls):
        """
        Create and return the connection string for your Azure
        PostgreSQL database per the AZURE_xxx environment variables.
        """
        return "host={} port={} dbname={} user={} password={} ".format(
            cls.postgresql_server(),
            cls.postgresql_port(),
            cls.postgresql_database(),
            cls.postgresql_user(),
            cls.postgresql_password(),
        )

    @classmethod
    def set_search_path_statement(cls):
        return 'SET search_path = ag_catalog, "$user", public;'

    @classmethod
    async def set_search_path(cls, conn):
        async with conn.cursor() as cursor:
            try:
                stmt = cls.set_search_path_statement()
                logging.info("PGUtil#set_search_path, stmt: {}".format(stmt))
                await cursor.execute(stmt)
                logging.info("PGUtil#set_search_path completed")
            except:
                pass

    @classmethod
    async def close_pool(cls) -> None:
        """
        Close the psycopg_pool.AsyncConnectionPool.
        """
        if PGUtil.pool is not None:
            logging.info("PGUtil#close_pool, closing...")
            await PGUtil.pool.close()
            logging.info("PGUtil#close_pool, closed")
            PGUtil.pool = None

    @classmethod
    async def execute_query(cls, sql) -> list:
        """
        Execute the given SQL query and return the results
        as a list of tuples.
        """
        stmt = sql.replace("\r\n", "")
        if len(stmt) > 400:
            # truncate long sql values for logging, such as with embeddings
            logging.info("PGUtil#execute_query, stmt: {} ...".format(stmt[0:400]))
        else:
            logging.info("PGUtil#execute_query, stmt: {}".format(stmt))
        result_objects = list()

        async with cls.pool.connection() as conn:
            stmt = sql.replace("\r\n", "")
            async with conn.cursor() as cursor:
                try:
                    await asyncio.wait_for(
                        cursor.execute(stmt), timeout=30.0
                    )  # timeout in seconds
                    results = await cursor.fetchall()
                    for row in results:
                        result_objects.append(row)
                except Exception as e:
                    logging.critical((str(e)))
        return result_objects


    @classmethod
    async def execute_insert(cls, 
        tablename: str, columns: list[str], values_tup: tuple) -> int:
        rowcount = 0
        if (len(columns) != len(values_tup)):
            logging.error("PGUtil#execute_insert, columns and values_tup length mismatch")
            return rowcount
        placeholders_list = list()
        for colname in columns:
            placeholders_list.append("%s")
        sql = "INSERT INTO {} ({}) VALUES ({});".format(
            tablename,
            ", ".join(columns),
            ", ".join(placeholders_list))
        logging.error("PGUtil#execute_insert, sql: {}".format(sql))

        async with cls.pool.connection() as conn:
            async with conn.cursor() as cursor:
                try:
                    await asyncio.wait_for(
                        cursor.execute(sql, values_tup), timeout=30.0)
                    rowcount = cursor.rowcount
                except Exception as e:
                    logging.critical((str(e)))
        return rowcount
