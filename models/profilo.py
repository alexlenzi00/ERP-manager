from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass
from db import diff_full

@dataclass
class Profilo(BaseModel):
	i_fk_profilo: int
	macro: list[int]
	campi: list[str]

	def to_sql(self, db) -> list[str]:
		sql: list[str] = []

		before_m = db.fetchall("SELECT DISTINCT I_FK_PROFILO, I_FK_MACRO FROM ER_MACRO_PROFILI WHERE I_FK_PROFILO = ?", (self.i_fk_profilo,))
		after_m = [ {"I_FK_PROFILO": int(self.i_fk_profilo), "I_FK_MACRO": int(m)} for m in self.macro ]
		sql += diff_full(before_m, after_m, id_cols=("I_FK_PROFILO", "I_FK_MACRO"), table="ER_MACRO_PROFILI")

		before_c = db.fetchall("SELECT DISTINCT I_FK_PROFILO, I_FK_MACRO, I_FK_CAMPO FROM ER_CAMPI_PROFILI WHERE I_FK_PROFILO = ?",(self.i_fk_profilo,))
		after_c = [ {"I_FK_PROFILO": int(self.i_fk_profilo), "I_FK_MACRO": int(c.split(".")[0]), "I_FK_CAMPO": int(c.split(".")[1])} for c in self.campi ]
		sql += diff_full(before_c, after_c, id_cols=("I_FK_PROFILO", "I_FK_MACRO", "I_FK_CAMPO"), table="ER_CAMPI_PROFILI")

		return sql

class FormProfili(BaseForm):
	i_fk_profilo = SelectField("Profilo", coerce=int, validators=[DataRequired()])
	macro = SelectMultipleField(coerce=str)
	campi = SelectMultipleField(coerce=str)

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
		super().__init__("Salva")

		rows = db.fetchall("SELECT I_ID, A_NOME FROM PROFILO ORDER BY A_NOME")
		self.i_fk_profilo.choices = [self._get(r, "I_ID", "A_NOME") for r in rows]

		if not selected_id and self.i_fk_profilo.choices:
			selected_id = self.i_fk_profilo.choices[0][0]
		self.i_fk_profilo.data = selected_id

		macro_all = db.fetchall("SELECT I_PK_MACRO, A_DESC_MACRO FROM ER_MACRO ORDER BY A_DESC_MACRO")
		macro_link = db.fetchall("SELECT I_FK_MACRO FROM ER_MACRO_PROFILI WHERE I_FK_PROFILO = ?", (selected_id,))
		linked_ids = {str(self._get(r, "I_FK_MACRO", "I_FK_MACRO")[0]) for r in macro_link}

		self.macro.choices = [(str(mid), desc) for mid, desc in (self._get(r, "I_PK_MACRO", "A_DESC_MACRO") for r in macro_all)]

		if not self.is_submitted():
			self.macro.data = list(linked_ids)

		self.macro_linked = [(mid, desc) for mid, desc in self.macro.choices if mid in linked_ids]

		campi_all = db.fetchall("SELECT CONCAT(I_FK_MACROSHOW, '.', I_PK_CAMPO) AS I_PK_CAMPO, A_DESC_CAMPO FROM ER_CAMPI ORDER BY A_DESC_CAMPO")
		campi_link = db.fetchall("SELECT CONCAT(I_FK_MACRO, '.', I_FK_CAMPO) AS I_FK_CAMPO FROM ER_CAMPI_PROFILI WHERE I_FK_PROFILO = ?", (selected_id,))
		linked_c = {str(self._get(r, "I_FK_CAMPO", "I_FK_CAMPO")[0]) for r in campi_link}

		self.campi.choices = [(str(cid), desc) for cid, desc in (self._get(r, "I_PK_CAMPO", "A_DESC_CAMPO") for r in campi_all)]

		if not self.is_submitted():
			self.campi.data = list(linked_c)

		self.campi_linked = [(cid, desc) for cid, desc in self.campi.choices if cid in linked_c]
