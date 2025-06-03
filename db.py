from typing import Sequence, Mapping, Any, List, Dict
from collections.abc import Iterable
import pyodbc
import json

def sqlStr(val):
	if val is None:
		return 'NULL'
	elif isinstance(val, str):
		return f'\'{val.replace('\'', '\'\'')}\''
	elif isinstance(val, int):
		return str(val)
	elif isinstance(val, float):
		return str(val).replace(',', '.')
	else:
		raise ValueError(f'Unsupported type: {type(val)}')

class DB:
	def __init__(self):
		self.cnxn_str = None
		self.cnxn = None

	def init_from_file(self, path):
		with open(path) as f:
			self.config = json.load(f)
		self.server = self.config['db']['server']
		self.username = self.config['db']['username']
		self.password = self.config['db']['password']
		self.database = self.config['db']['database']
		self.cnxn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
		self.cnxn = pyodbc.connect(self.cnxn_str, autocommit=True)

	def fetchall(self, sql, params=()):
		cur = self.cnxn.cursor()
		cur.execute(sql, params)
		cols = [c[0] for c in cur.description]
		return [dict(zip(cols, row)) for row in cur.fetchall()]

	def fetchone(self, sql, params=()):
		rows = self.fetchall(sql, params)
		return rows[0] if rows else None

	def next_pk(self, table, pk_field):
		row = self.fetchone(f'SELECT ISNULL(MAX({pk_field}),0)+1 AS nxt FROM {table}')
		return row['nxt'] if row else 1

def _chiave(riga: Dict[str, Any], id_cols: Sequence[str]) -> List[Any]:
	'''
	Ritorna i valori delle colonne di chiave primaria di una riga.
	'''
	return [riga[k] for k in id_cols if k in riga]

def _trova(righe: List[Dict[str, Any]], chiave: List[Any], id_cols: Sequence[str]) -> Dict[str, Any] | None:
	'''
	Ritorna la riga che ha la chiave primaria specificata.
	'''
	for riga in righe:
		if _chiave(riga, id_cols) == chiave:
			return riga
	return None

def diff_full(before: Sequence[Dict[str, Any]], after: Sequence[Dict[str, Any]], *, id_cols: Sequence[str], table: str) -> List[str]:
	'''
	Confronta due insiemi di righe (dict) e genera:
		• INSERT - presenti solo in `after`
		• UPDATE - presenti in entrambi ma con valori diversi
		• DELETE - presenti solo in `before`
	'''
	sql: list[str] = []

	before = sorted(before, key=lambda r: tuple(r[c] for c in id_cols))
	after = sorted(after, key=lambda r: tuple(r[c] for c in id_cols))

	delete_keys = [k for k in before if _trova(after, _chiave(k, id_cols), id_cols) is None]
	insert_keys = [k for k in after if _trova(before, _chiave(k, id_cols), id_cols) is None]
	update_keys = [k for k in after if _trova(before, _chiave(k, id_cols), id_cols) is not None and k != _trova(before, _chiave(k, id_cols), id_cols)]

	print(f'before = {before}')
	print(f'after = {after}')
	print(f'delete keys: {delete_keys}')
	print(f'insert keys: {insert_keys}')
	print(f'update keys: {update_keys}')
	print('\n\n')

	for d in delete_keys:
		sql.append(f'DELETE FROM {table} WHERE {' AND '.join(f'{c} = {sqlStr(d[c])}' for c in id_cols)};')

	for i in insert_keys:
		campi = []
		values = []
		for col in i:
			campi.append(col)
			values.append(sqlStr(i[col]))
		sql.append(f'INSERT INTO {table} ({', '.join(campi)}) VALUES ({', '.join(values)});')

	for u in update_keys:
		campi = []
		campiK = []
		values = []
		valuesK = []
		for col in u:
			if col in id_cols:
				campiK.append(col)
				valuesK.append(sqlStr(u[col]))
			else:
				campi.append(col)
				values.append(sqlStr(u[col]))

		sql.append(f'UPDATE {table} SET {', '.join(f'{c} = {v}' for c, v in zip(campi, values))} WHERE {' AND '.join(f'{c} = {v}' for c, v in zip(campiK, valuesK))};')

	return sql

def elenco_colonne(db, table: str) -> List[str]:
	'''
	Ritorna l'elenco delle colonne di una tabella.
	'''

	qry = 'SELECT DISTINCT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = \'dbo\' AND TABLE_NAME = ? ORDER BY COLUMN_NAME'

	rows = db.fetchall(qry, (table,))
	return [row['COLUMN_NAME'] for row in rows] if rows else []