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

class TableEntryForm(BaseForm):
	tabella = SelectField('Tabella', choices=[], coerce=int, validators=[DataRequired()])
	ordine = IntegerField('Ordine', validators=[DataRequired()])
	obbligatorio = SelectField('Obbligatorio', choices=[('N', 'No'), ('S', 'Si')], coerce=str, default='N', validators=[DataRequired()])

class FormMacro(BaseForm):
	i_pk_macro = IntegerField('PK Macro', validators=[DataRequired()], render_kw={'readonly': True})
	a_desc_macro = StringField('Nome Macro', validators=[DataRequired()])
	i_ordine = IntegerField('Ordine', validators=[DataRequired()], render_kw={'readonly': True})
	tables = FieldList(FormField(TableEntryForm), min_entries=1)

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		table_choices = [(-1, '. . .')] + [(int(r['ID']), r['TABELLA']) for r in db.fetchall("SELECT I_PK_TABELLA AS ID, A_NOME_TABELLA AS TABELLA FROM ER_TABELLE ORDER BY A_NOME_TABELLA")]

		TableEntryForm.tabella.choices = table_choices

		super().__init__(*args, submit_label=tasto, **kwargs)

		for entry in self.tables.entries:
			entry.tabella.choices = table_choices

		if not editing:
			self.i_pk_macro.data = db.next_pk('ER_MACRO', 'I_PK_MACRO')
			self.i_ordine.data = db.next_pk('ER_MACRO', 'I_PK_MACRO')
