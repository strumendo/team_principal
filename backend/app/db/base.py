"""
SQLAlchemy declarative base with naming conventions.
Base declarativa do SQLAlchemy com convencoes de nomenclatura.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Naming conventions for constraints / Convencoes de nomenclatura para constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Classe base para todos os modelos SQLAlchemy.
    """

    metadata = MetaData(naming_convention=convention)
