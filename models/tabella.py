from wtforms import StringField, IntegerField, SelectField, FieldList, FormField, HiddenField
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

class TableEntryForm(BaseForm):
	tabella = SelectField('Tabella', choices=[], coerce=int, validators=[DataRequired()])
	tipo_join = SelectField('Tipo Join', choices=[('I', 'INNER JOIN'), ('L', 'LEFT JOIN')], coerce=str, validators=[DataRequired()])
	vincolo = StringField('Vincolo', validators=[Optional()])

class FormTabelle(BaseForm):
	i_pk_tabella = IntegerField('PK Tabella', validators=[DataRequired()], render_kw={'readonly': True})
	a_nome_tabella = SelectField('Tabella', coerce=str, validators=[DataRequired()])
	a_desc_tabella = StringField('Descrizione', validators=[Optional()])
	tables = FieldList(FormField(TableEntryForm), min_entries=1)

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		table_choices = [(-1, '. . .')] + [(int(r['ID']), r['TABELLA']) for r in db.fetchall("SELECT I_PK_TABELLA AS ID, A_NOME_TABELLA AS TABELLA FROM ER_TABELLE ORDER BY A_NOME_TABELLA")]

		TableEntryForm.tabella.choices = table_choices

		super().__init__(*args, submit_label=tasto, **kwargs)

		for entry in self.tables.entries:
			entry.tabella.choices = table_choices

		rows = db.fetchall('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \'dbo\' ORDER BY TABLE_NAME')
		self.a_nome_tabella.choices = [(str(r['TABLE_NAME']), str(r['TABLE_NAME'])) for r in rows]
		if not editing:
			self.i_pk_tabella.data = db.next_pk('ER_TABELLE', 'I_PK_TABELLA')
