
import logging
import os

from typing import List
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON as pgJSON

from src.os.env import Env


# Class AppEngine is used to create and manage the singleton instance
# of the SQLAlchemy engine, created with the create_engine() function.

class AppEngine():
    
    engine = None

    @classmethod
    def initialize(cls):
        AppEngine.engine = cls.get_engine()

    @classmethod
    def get_engine(cls):
        if AppEngine.engine is None:
            try:
                engine_url = Env.sqlalchemy_engine_url()
                logging.info("AppEngine#engine_url: {}".format(engine_url))
                pool_size = Env.sqlalchemy_pool_size()
                max_overflow = Env.sqlalchemy_max_overflow()
                AppEngine.engine = create_engine(
                    engine_url, pool_size=pool_size, max_overflow=max_overflow)
            except Exception as e:
                print(str(e))
        print("AppEngine.get_engine, engine: {}".format(AppEngine.engine))
        return AppEngine.engine

    @classmethod
    def dispose(cls):
        if AppEngine.engine is not None:
            try:
                print("AppEngine.dispose()...")
                AppEngine.engine.dispose()
            except Exception as e:
                print("Error disposing AppEngine:")
                print(str(e))
            AppEngine.engine = None
            print("AppEngine.dispose() completed")


class Base(DeclarativeBase):
    pass

class Configuration(Base):
    __tablename__ = "configuration"

    name: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[pgJSON] = mapped_column(pgJSON, nullable=False)

    def __repr__(self) -> str:
        return f"Configuration(name={self.name!r}, data={self.data!r})"

