import pyodbc
import json

class DB:
	def __init__(self):
		self.cnxn_str = None
		self.cnxn = None
	def init_from_file(self, path):
		with open(path) as f:
			cfg = json.load(f)
		self.server = cfg["db"]["server"]
		self.username = cfg["db"]["username"]
		self.password = cfg["db"]["password"]
		self.database = cfg["db"]["database"]
		self.cnxn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
		self.cnxn = pyodbc.connect(self.cnxn_str, autocommit=True)
	def fetchall(self, sql, params=()):
		print(f"Executing SQL: {sql} with params: {params}")
		cur = self.cnxn.cursor()
		cur.execute(sql, params)
		cols = [c[0] for c in cur.description]
		return [dict(zip(cols, row)) for row in cur.fetchall()]
	def fetchone(self, sql, params=()):
		rows = self.fetchall(sql, params)
		return rows[0] if rows else None
	def next_pk(self, table, pk_field):
		row = self.fetchone(f"SELECT ISNULL(MAX({pk_field}),0)+1 AS nxt FROM {table}")
		return row["nxt"] if row else 1
