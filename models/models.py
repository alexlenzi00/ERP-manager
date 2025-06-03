from __future__ import annotations
from dataclasses import fields
from typing import ClassVar, List
from db import diff_full, sqlStr

class BaseModel:
	table: ClassVar[str]
	pk: ClassVar[List[str]]
	skip_cols: ClassVar[set[str]] = set()

	@classmethod
	def _cols(cls) -> tuple[str, ...]:
		return tuple(f.name for f in fields(cls) if f.init and f.name not in cls.skip_cols and f.name != 'skip_cols')

	def _before(self, db):
		return db.fetchall(f'SELECT * FROM {self.table} WHERE {' AND '.join([f'{k}={sqlStr(getattr(self, k))}' for k in self.pk if k not in self.skip_cols])}', ())

	def to_sql(self, db) -> list[str]:
		return diff_full(self._before(db), [{c: getattr(self, c) for c in self._cols()}], id_cols=self.pk, table=self.table)

	@classmethod
	def daForm(cls, form):
		return cls(**{c.upper(): getattr(form, c.lower()).data for c in cls._cols() if hasattr(form, c.lower())})