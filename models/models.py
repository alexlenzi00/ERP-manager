from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, List, Sequence
from sql_diff import diff_no_delete

class BaseModel:
	table: str
	pk: str
	cols: Sequence[str]

	def _before_rows(self, db, id_value):
		q = f"SELECT {', '.join(self.cols)} FROM {self.table} WHERE {self.pk} = ?"
		return db.fetchall(q, (id_value,))

	def to_sql(self, db) -> list[str]:
		before = self._before_rows(db, self.pk)
		after = [ {c for c in self.cols} ]

		return diff_no_delete(
			before, after,
			id_col=self.pk,
			table=self.table,
			cols=self.cols
		)