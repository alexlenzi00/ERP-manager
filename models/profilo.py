from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass
from db import diff_full

@dataclass
class Profilo(BaseModel):
	I_ID: int
	MACRO: list[int]
	CAMPI: list[str]

	def to_sql(self, db) -> list[str]:
		sql: list[str] = []

		before_m = db.fetchall('SELECT DISTINCT I_FK_PROFILO, I_FK_MACRO FROM ER_MACRO_PROFILI WHERE I_FK_PROFILO = ?', (self.I_ID,))
		after_m = [ {'I_FK_PROFILO': int(self.I_ID), 'I_FK_MACRO': int(m)} for m in self.MACRO ]
		sql += diff_full(before_m, after_m, id_cols=('I_FK_PROFILO', 'I_FK_MACRO'), table='ER_MACRO_PROFILI')

		before_c = db.fetchall('SELECT DISTINCT I_FK_PROFILO, I_FK_MACRO, I_FK_CAMPO FROM ER_CAMPI_PROFILI WHERE I_FK_PROFILO = ?',(self.I_ID,))
		after_c = [ {'I_FK_PROFILO': int(self.I_ID), 'I_FK_MACRO': int(c.split('.')[0]), 'I_FK_CAMPO': int(c.split('.')[1])} for c in self.CAMPI ]
		sql += diff_full(before_c, after_c, id_cols=('I_FK_PROFILO', 'I_FK_MACRO', 'I_FK_CAMPO'), table='ER_CAMPI_PROFILI')

		return sql

class FormProfili(BaseForm):
	i_id = IntegerField('ID Profilo', validators=[DataRequired()], render_kw={'readonly': True})
	a_nome = StringField('Profilo', validators=[DataRequired()], render_kw={'readonly': True})
	macro = SelectMultipleField(validators=[Optional()], render_kw={'data-placeholder': 'Seleziona le macro'})
	campi = SelectMultipleField(validators=[Optional()], render_kw={'data-placeholder': 'Seleziona i campi'})

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		super().__init__(*args, **kwargs, submit_label=tasto)

		m_all = db.fetchall('SELECT I_PK_MACRO, A_DESC_MACRO FROM ER_MACRO ORDER BY 1')
		m_link = db.fetchall('SELECT I_FK_MACRO FROM ER_MACRO_PROFILI WHERE I_FK_PROFILO = ?', (self.i_id.data,))

		print(f'\n\nProfilo {self.i_id.data} - Macro: {m_link}')
		print(f'Args: {args}, Kwargs: {kwargs}\n\n')

		self.macro.choices = [(str(m['I_PK_MACRO']), f'{m['I_PK_MACRO']} - {m['A_DESC_MACRO']}') for m in m_all]
		if not self.is_submitted():
			self.macro.data = list(str(m['I_FK_MACRO']) for m in m_link)

		c_all = db.fetchall('SELECT CONCAT(I_FK_MACROSHOW, \'.\', I_PK_CAMPO) AS I_PK_CAMPO, A_DESC_CAMPO FROM ER_CAMPI ORDER BY A_DESC_CAMPO')
		c_link = db.fetchall('SELECT CONCAT(I_FK_MACRO, \'.\', I_FK_CAMPO) AS I_FK_CAMPO FROM ER_CAMPI_PROFILI WHERE I_FK_PROFILO = ?', (self.i_id.data,))

		self.campi.choices = [(str(c['I_PK_CAMPO']), str(c['A_DESC_CAMPO'])) for c in c_all]
		if not self.is_submitted():
			self.campi.data = list(str(c['I_FK_CAMPO']) for c in c_link)
