class SQLGenerator:
	def _insert(self, table:str, values:dict):
		cols = ", ".join(values.keys())
		vals = ", ".join([self._fmt(v) for v in values.values()])
		return f"INSERT INTO {table} ({cols}) VALUES ({vals});"

	def _fmt(self, v):
		if v is None or v=='' or v==-1:
			return "NULL"
		if isinstance(v, str):
			return "N'"+v.replace("'","''")+"'"
		return str(v).replace(",", ".")

	def build_sql(self, pending:dict, db):
		parts = ["-- Patch generata il "+datetime.datetime.now().isoformat()]
		order = ["tabella","macro","gruppo","profilo","campo"]
		for ent in order:
			for item in pending.get(ent, []):
				if ent=="campo":
					parts.append(self._insert("ER_CAMPI", item))
				elif ent=="tabella":
					parts.append(self._insert("ER_TABELLE", item))
				elif ent=="macro":
					parts.append(self._insert("ER_MACRO", item))
				elif ent=="gruppo":
					parts.append(self._insert("ER_GRUPPI", item))
				elif ent=="profilo":
					parts.append(self._insert("ER_MACRO_PROFILI", item))
		return "\n".join(parts)
