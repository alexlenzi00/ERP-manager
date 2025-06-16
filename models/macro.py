from wtforms import StringField, IntegerField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Macro(BaseModel):
	I_PK_MACRO: int
	A_DESC_MACRO: str
	I_ORDINE: int = 0

	table = 'ER_MACRO'
	pk = ['I_PK_MACRO']

class FormMacro(BaseForm):
	class TableEntryForm(BaseForm):
		tabella = SelectField('Tabella', coerce=int, validators=[DataRequired()])
		ordine = HiddenField('Ordine')

	i_pk_macro = IntegerField('PK Macro', validators=[DataRequired()], render_kw={'readonly': True})
	a_desc_macro = StringField('Nome Macro', validators=[DataRequired()])
	i_ordine = IntegerField('Ordine', validators=[DataRequired()], render_kw={'readonly': True})
	tables = FieldList(FormField(TableEntryForm), min_entries=0)

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		super().__init__(*args, **kwargs, submit_label=tasto)
		table_choices = [(int(r['ID']), str(r['TABELLA'])) for r in db.fetchall("SELECT I_PK_TABELLA AS ID, A_NOME_TABELLA AS TABELLA FROM ER_TABELLE ORDER BY 2")]
		for entry in self.tables:
			entry.form.tabella.choices = table_choices

		if not editing:
			self.i_pk_macro.data = db.next_pk('ER_MACRO', 'I_PK_MACRO')
			self.i_ordine.data = db.next_pk('ER_MACRO', 'I_PK_MACRO')
