from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from forms import BaseForm
from models import BaseModel
from dataclasses import dataclass

@dataclass
class Profilo(BaseModel):
	profilo_id: int
	macro: list[int]
	macro_fk: list[int]
	campi: list[int]

	@classmethod
	def daForm(cls, form) -> "Profilo":
		return cls(
			profilo_id = form.id_profilo.data,
			macro = [int(m) for m in form.macro.data],
			macro_fk = [int(m.split('.')[0]) for m in form.macro.data],
			campi = [int(c.split('.')[1]) for c in form.campi.data],
		)

	def to_sql(self, db) -> list[str]:
		sql: list[str] = []

		before_m = db.fetchall(
			"SELECT DISTINCT I_FK_PROFILO, I_FK_MACRO FROM ER_MACRO_PROFILI WHERE I_FK_PROFILO = ?",
			(self.profilo_id,)
		)
		after_m = [ {"I_FK_PROFILO": self.profilo_id, "I_FK_MACRO": m}
					for m in self.macro ]

		sql += diff_no_delete(
			before_m, after_m,
			id_col="I_FK_MACRO",
			table="ER_MACRO_PROFILI",
			cols=("I_FK_PROFILO", "I_FK_MACRO")
		)

		before_c = db.fetchall(
			"SELECT DISTINCT I_FK_PROFILO, I_FK_MACRO, I_FK_CAMPO FROM ER_CAMPI_PROFILI WHERE I_FK_PROFILO = ?",
			(self.profilo_id,)
		)

		print(f"before_c: {before_c}")

		after_c = [ {"I_FK_PROFILO": self.profilo_id, "I_FK_MACRO": m, "I_FK_CAMPO": c}
					for m, c in zip(self.macro_fk, self.campi) ]

		print(f"after_c: {after_c}")

		sql += diff_no_delete(
			before_c, after_c,
			id_col="I_FK_CAMPO",
			table="ER_CAMPI_PROFILI",
			cols=("I_FK_PROFILO", "I_FK_MACRO", "I_FK_CAMPO")
		)

		return sql

class FormProfili(FlaskForm):
	id_profilo = SelectField("Profilo", coerce=int, validators=[DataRequired()])
	macro = SelectMultipleField(coerce=str)
	campi = SelectMultipleField(coerce=str)
	submit = SubmitField("Salva")

	@staticmethod
	def _get(row, id_col, desc_col):
		if isinstance(row, dict):
			if '.' in str(row[id_col]):
				return float(row[id_col]), str(row[desc_col])
			return int(row[id_col]), str(row[desc_col])
		try:
			return int(getattr(row, id_col)), str(getattr(row, desc_col))
		except AttributeError:
			rid, rdesc = row[:2]
			return int(rid), str(rdesc)

	def __init__(self, db, selected_id: int | None = None, *args, **kwa):
		super().__init__(*args, **kwa)

		rows = db.fetchall("SELECT I_ID, A_NOME FROM PROFILO ORDER BY A_NOME")
		self.id_profilo.choices = [self._get(r, "I_ID", "A_NOME") for r in rows]

		if not selected_id and self.id_profilo.choices:
			selected_id = self.id_profilo.choices[0][0]
		self.id_profilo.data = selected_id

		macro_all = db.fetchall("SELECT I_PK_MACRO, A_DESC_MACRO FROM ER_MACRO ORDER BY A_DESC_MACRO")
		macro_link = db.fetchall(
			"SELECT I_FK_MACRO FROM ER_MACRO_PROFILI WHERE I_FK_PROFILO = ?", (selected_id,)
		)
		linked_ids = {str(self._get(r, "I_FK_MACRO", "I_FK_MACRO")[0]) for r in macro_link}

		self.macro.choices = [
			(str(mid), desc)
			for mid, desc in (self._get(r, "I_PK_MACRO", "A_DESC_MACRO") for r in macro_all)
		]

		if not self.is_submitted():
			self.macro.data = list(linked_ids)

		self.macro_linked = [(mid, desc) for mid, desc in self.macro.choices if mid in linked_ids]

		campi_all = db.fetchall("SELECT CONCAT(I_FK_MACROSHOW, '.', I_PK_CAMPO) AS I_PK_CAMPO, A_DESC_CAMPO FROM ER_CAMPI ORDER BY A_DESC_CAMPO")
		campi_link = db.fetchall(
			"SELECT CONCAT(I_FK_MACRO, '.', I_FK_CAMPO) AS I_FK_CAMPO FROM ER_CAMPI_PROFILI WHERE I_FK_PROFILO = ?", (selected_id,)
		)
		linked_c = {str(self._get(r, "I_FK_CAMPO", "I_FK_CAMPO")[0]) for r in campi_link}

		self.campi.choices = [
			(str(cid), desc)
			for cid, desc in (self._get(r, "I_PK_CAMPO", "A_DESC_CAMPO") for r in campi_all)
		]

		if not self.is_submitted():
			self.campi.data = list(linked_c)

		self.campi_linked = [(cid, desc) for cid, desc in self.campi.choices if cid in linked_c]
