from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Tabella(BaseModel):
	I_PK_TABELLA: int
	A_NOME_TABELLA: str
	A_DESC_TABELLA: str = ''

	table = 'ER_TABELLE'
	pk = ['I_PK_TABELLA']

class FormTabelle(BaseForm):
	i_pk_tabella = IntegerField('PK Tabella', validators=[DataRequired()], render_kw={'readonly': True})
	a_nome_tabella = SelectField('Tabella', coerce=str, validators=[DataRequired()])
	a_desc_tabella = StringField('Descrizione', validators=[Optional()])

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		super().__init__(*args, **kwargs, submit_label=tasto)
		rows = db.fetchall('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \'dbo\' ORDER BY TABLE_NAME')
		self.a_nome_tabella.choices = [(str(r['TABLE_NAME']), str(r['TABLE_NAME'])) for r in rows]
		if not editing:
			self.i_pk_tabella.data = db.next_pk('ER_TABELLE', 'I_PK_TABELLA')
