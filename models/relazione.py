from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Relazione(BaseModel):
	I_FK_TABELLA1: int
	I_FK_TABELLA2: int
	A_TIPO_JOIN: str
	A_VINCOLO: str

	table = 'ER_RELAZIONI'
	pk = ['I_FK_TABELLA1', 'I_FK_TABELLA2']

	@classmethod
	def daForm(cls, form) -> 'Tabella':
		data = {c: getattr(form, c).data for c in cls.cols if hasattr(form, c)}
		return cls(**data)

class FormTabelle(BaseForm):
	i_pk_tabella = IntegerField('PK Tabella', validators=[DataRequired()])
	a_nome_tabella = SelectField('Tabella', coerce=str, validators=[DataRequired()])
	a_desc_tabella = StringField('Descrizione', validators=[Optional()])

	def __init__(self, db, editing=False, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.i_pk_tabella.data = db.next_pk('ER_TABELLE', 'I_PK_TABELLA')
		rows = db.fetchall('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \'dbo\' ORDER BY TABLE_NAME')
		self.a_nome_tabella.choices = [(str(r['TABLE_NAME']), str(r['TABLE_NAME'])) for r in rows]
