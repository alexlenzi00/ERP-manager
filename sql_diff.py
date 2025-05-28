from collections.abc import Iterable
from typing import Any, Sequence

def _row_tuple(row: Any, id_col: str | int, *cols: str | int) -> tuple:
	"""dict | named-tuple | tuple → tuple hashable con pk + colonne."""
	if isinstance(row, dict):
		return tuple(row[k] for k in (id_col, *cols))
	try:
		return tuple(getattr(row, k) for k in (id_col, *cols))
	except AttributeError:
		return tuple(row[k] for k in (id_col, *cols))

def diff_no_delete(
	before: Sequence[Any],
	after:  Sequence[Any],
	*,
	id_col: str | int,
	table: str,
	cols:   Sequence[str]
) -> list[str]:
	"""
	Ritorna solo INSERT e (se la riga esiste già) UPDATE.
	Nessuna DELETE viene mai prodotta.
	`cols` = colonne (inserite / aggiornate) **ordinante come nel DB**.
	"""
	bmap = { _row_tuple(r, id_col, *cols): r for r in before }
	amap = { _row_tuple(r, id_col, *cols): r for r in after  }

	sql: list[str] = []
	col_list = ", ".join(cols)

	for key, row in amap.items():
		pk = key[0]

		if key not in bmap:
			values = ", ".join(_q(row, c) for c in cols)
			sql.append(f"INSERT INTO {table} ({col_list}) VALUES ({values});")

	return sql

def _q(row: Any, c: str | int) -> str:
	v = row[c] if isinstance(row, dict) else getattr(row, c, row[c])
	if v is None:
		return "NULL"
	if isinstance(v, (int, float)):
		return str(v).replace(",", ".")
	return "'" + str(v).replace("'", "''") + "'"
