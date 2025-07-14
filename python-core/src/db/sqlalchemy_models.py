import os

from typing import List
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON as pgJSON
from sqlalchemy import create_engine


class AppEngine():
    
    engine = None

    @classmethod
    def initialize(cls):
        AppEngine.engine = cls.get_engine()

    @classmethod
    def get_engine(cls):
        if AppEngine.engine is None:
            try:
                engine_url = AppEngine.get_engine_url()
                pool_size = 5     # TODO make this configurable
                max_overflow = 0  # TODO make this configurable
                AppEngine.engine = create_engine(
                    engine_url, pool_size=pool_size, max_overflow=max_overflow)
            except Exception as e:
                print(str(e))
        print("AppEngine.get_engine, engine: {}".format(AppEngine.engine))
        return AppEngine.engine

   
    @classmethod
    def get_engine_url(cls) -> str:
        """
        Create and return a SQLAlchemy engine URL for your PostgreSQL database.
        The return value can be passed to the SQLAlchemy create_engine() function.
        """
         # "postgresql+psycopg2://user:password@hostname:port/database_name")
        return "postgresql+psycopg://{}:{}@{}:{}/{}".format(
            cls.postgresql_user(),
            cls.postgresql_password(),
            cls.postgresql_server(),
            cls.postgresql_port(),
            cls.postgresql_database(),
        )
    
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


class Base(DeclarativeBase):
    pass

class Configuration(Base):
    __tablename__ = "configuration"

    name: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[pgJSON] = mapped_column(pgJSON, nullable=False)

    def __repr__(self) -> str:
        return f"Configuration(name={self.name!r}, data={self.data!r})"

