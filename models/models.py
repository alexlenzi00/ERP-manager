from __future__ import annotations
from dataclasses import dataclass, asdict, fields
from typing import ClassVar, List, Sequence
from db import diff_full

class BaseModel:
	table: ClassVar[str]
	pk: ClassVar[List[str]]
	skip_cols: ClassVar[set[str]] = set()

	@classmethod
	def _cols(cls) -> tuple[str, ...]:
		return tuple(
			f.name for f in fields(cls)
			if f.init and f.name not in cls.skip_cols
		)

	def _before(self, db):
		q = f"SELECT {', '.join(self._cols())} FROM {self.table} WHERE {self.pk}=?"
		return db.fetchall(q, (getattr(self, self.pk),))

	def to_sql(self, db) -> list[str]:
		before = self._before(db)
		after  = [{c: getattr(self, c) for c in self._cols()}]
		return diff_full(before, after, id_cols=self.pk, table=self.table)

	@classmethod
	def daForm(cls, form):
		data = {c: getattr(form, c).data for c in cls._cols() if hasattr(form, c)}
		return cls(**data)
