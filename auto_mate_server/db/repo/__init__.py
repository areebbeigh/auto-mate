from contextlib import contextmanager
from typing import Type, Iterator, Tuple

from sqlalchemy.orm import Session

from .base import BaseRepo
from auto_mate_server.db.session import get_db_ctx


@contextmanager
def get_repos(*klasses: Type[BaseRepo]) -> Iterator[Tuple[Session, ...]]:
    with get_db_ctx() as db:
        repos = []
        for klass in klasses:
            repos.append(klass(db))
        yield (db, *repos)
