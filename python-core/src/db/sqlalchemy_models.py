import asyncio
import json
import logging
import os

from datetime import datetime
from typing import List
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy import select
from sqlalchemy.orm import Session

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON as pgJSON

from src.os.env import Env

# This module contains classes and SQLAlchemy ORM models 
# that are used to access the Azure PostgreSQL database. 
#
# Though SQLAlchemy is capable of additionally creating the tables
# and indexes for the database, this application currently uses a
# traditional DDL file instead; see file 'sql/ai_pipeline.ddl'
#  
class AppEngine():
    """
    Class AppEngine is used to create and manage the singleton instance
    of the SQLAlchemy engine, created with the create_engine() function.
    """
    engine = None  # singleton instance of the SQLAlchemy engine

    @classmethod
    def initialize(cls):
        AppEngine.engine = cls.get_engine()

    @classmethod
    def get_engine(cls):
        """ Lazy initialization getter method for the SQLAlchemy engine singleton. """
        if AppEngine.engine is None:
            try:
                engine_url = Env.sqlalchemy_engine_url()
                logging.info("AppEngine#engine_url: {}".format(engine_url))
                pool_size = Env.sqlalchemy_pool_size()
                max_overflow = Env.sqlalchemy_max_overflow()
                AppEngine.engine = create_engine(
                    engine_url, pool_size=pool_size, max_overflow=max_overflow)
            except Exception as e:
                logging.critical(str(e))
        logging.info("AppEngine.get_engine, engine: {}".format(AppEngine.engine))
        return AppEngine.engine
 
    @classmethod
    def dispose(cls):
        """ Close or dispose of the SQLAlchemy engine object. """
        if AppEngine.engine is not None:
            try:
                logging.error("AppEngine.dispose()...")
                AppEngine.engine.dispose()
            except Exception as e:
                logging.error("Error disposing AppEngine:")
                logging.error(str(e))
            AppEngine.engine = None
            logging.warning("AppEngine.dispose() completed")


class Base(DeclarativeBase):
    pass


class Configuration(Base):
    __tablename__ = "configuration"
    ##__table_args__ = {'extend_existing': True}

    name: Mapped[str] = mapped_column(primary_key=True)
    data: Mapped[pgJSON] = mapped_column(pgJSON, nullable=False)

    def __repr__(self) -> str:
        return json.dumps(self.as_dict())
    
    def as_dict(self) -> dict:
        d = dict()
        d["name"] = self.name
        d["data"] = self.data
        return d
    

class Document(Base):
    __tablename__ = "documents"
    #__table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    source_system: Mapped[str] = mapped_column(String(128))
    source_path: Mapped[str] = mapped_column(String(1024))
    raw_container: Mapped[str] = mapped_column(String(64))
    raw_file_name: Mapped[str] = mapped_column(String(128))
    raw_file_size: Mapped[int] = mapped_column(Integer)
    raw_etag: Mapped[str] = mapped_column(String(32))
    raw_file_type: Mapped[str] = mapped_column(String(128))
    raw_storage_path: Mapped[str] = mapped_column(String(1024))
    raw_inserted_at: Mapped[datetime] = mapped_column(DateTime)
    processing_state: Mapped[str] = mapped_column(String(64))
    preprocessed_container: Mapped[str] = mapped_column(String(64))
    preprocessed_path: Mapped[str] = mapped_column(String(1024))
    preprocessing_chunk_count: Mapped[int] = mapped_column(Integer)
    preprocessing_messages: Mapped[pgJSON] = mapped_column(pgJSON)
    preprocessed_at: Mapped[datetime] = mapped_column(DateTime)
    qna_extracted_at: Mapped[datetime] = mapped_column(DateTime)
    qna_extracted_messages: Mapped[pgJSON] = mapped_column(pgJSON)

    def __repr__(self) -> str:
        return json.dumps(self.as_dict())

    def as_dict(self) -> dict:
        d = dict()
        d["id"] = self.id
        d["source_system"] = self.source_system
        d["source_path"] = self.source_path
        d["raw_container"] = self.raw_container
        d["raw_file_name"] = self.raw_file_name
        d["raw_file_size"] = self.raw_file_size
        d["raw_etag"] = self.raw_etag
        d["raw_file_type"] = self.raw_file_type
        # d["raw_storage_path"] = self.raw_storage_path
        # d["raw_inserted_at"] = self.raw_inserted_at.isoformat()
        # d["processing_state"] = self.processing_state
        # d["preprocessed_container"] = self.preprocessed_container
        # d["preprocessed_path"] = self.preprocessed_path
        # d["preprocessing_chunk_count"] = self.preprocessing_chunk_count
        # d["preprocessing_messages"] = self.preprocessing_messages
        # d["preprocessed_at"] = self.preprocessed_at.isoformat() if self.preprocessed_at else None
        # d["qna_extracted_at"] = self.qna_extracted_at.isoformat()
        # d["qna_extracted_messages"] = self.qna_extracted_messages
        return d

class ExtractedQA(Base):
    __tablename__ = "extracted_qa"
    #__table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: Define the fields for the ExtractedQA model


class TeamsQA(Base):
    __tablename__ = "teams_qa"
    #__table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: Define the fields for the TeamsQA model


class ApplicationEvent(Base):
    __tablename__ = "application_events"
    #__table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    # TODO: Define the fields for the ApplicationEvent model


class CommonOperations():
    """
    Common database operations that can be used thoughtout the application
    in a reusable way.
    """
    
    @classmethod
    async def read_configuration_object(cls, config_name: str) -> dict:
        """
        Read the given configuration, from the DB, by its name, such as 'ai_pipeline'.
        Return the JSON object from the JSONB 'data' column.
        TODO: Consider returning a Pydantic model instead of a dict.
        """
        await asyncio.sleep(0.1)  # Simulate some async work for now
        obj = None
        try:
            stmt = select(Configuration).where(Configuration.name == config_name)
            with Session(AppEngine.get_engine()) as session:
                c = session.execute(stmt).scalar_one_or_none()
                obj = c.data
        except Exception as e:
            logging.critical(str(e))
        return obj
    
    @classmethod
    async def read_document(cls, d: Document):
        await asyncio.sleep(0.1)  # Simulate some async work for now
        obj = None
        try:
            stmt = select(Document).where(
                Document.source_system == d.source_system,
                Document.source_path   == d.source_path,
                Document.raw_container == d.raw_container,
                Document.raw_file_name == d.raw_file_name
            )
            with Session(AppEngine.get_engine()) as session:
                obj = session.execute(stmt).scalar_one_or_none()
        except Exception as e:
            logging.critical(str(e))
        return obj
