import abc
from typing import Generic, TypeVar, Type
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy import select

from auto_mate_server.db.models import Base

T = TypeVar("T")


class BaseRepo(Generic[T]):
    def __init__(self, session: Session) -> None:
        self.session = session

    @classmethod
    @abc.abstractmethod
    def get_model(cls) -> type[T]:
        pass

    def filter(self, clause, joins=[]) -> list[T]:
        expr = select(self.get_model())
        if joins:
            for j in joins:
                expr = expr.join(j)
        if clause:
            expr = expr.where(clause)

        return self.session.scalars(expr)
