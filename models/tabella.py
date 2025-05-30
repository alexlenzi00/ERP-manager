from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Tabella(BaseModel):
	I_PK_TABELLA: int
	A_NOME_TABELLA: str
	A_DESC_TABELLA: str

	table = 'ER_TABELLE'
	pk = ['I_PK_TABELLA']
	cols = ('I_PK_TABELLA', 'A_NOME_TABELLA', 'A_DESC_TABELLA')

	@classmethod
	def daForm(cls, form) -> 'Tabella':
		data = {c: getattr(form, c).data for c in cls.cols if hasattr(form, c)}
		return cls(**data)

class FormTabelle(BaseForm):
	i_pk_tabella = IntegerField('PK Tabella', validators=[DataRequired()])
	a_nome_tabella = SelectField('Tabella', coerce=str, validators=[DataRequired()])
	a_desc_tabella = StringField('Descrizione', validators=[Optional()])

	def __init__(self, db, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.i_pk_tabella.data = db.next_pk('ER_TABELLE', 'I_PK_TABELLA')
		rows = db.fetchall("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo' ORDER BY TABLE_NAME")
		self.a_nome_tabella.choices = [(str(r['TABLE_NAME']), str(r['TABLE_NAME'])) for r in rows]
