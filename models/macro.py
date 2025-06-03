from wtforms import StringField, IntegerField
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
	i_pk_macro = IntegerField('PK Macro', validators=[DataRequired()], render_kw={'readonly': True})
	a_desc_macro = StringField('Nome Macro', validators=[DataRequired()])
	i_ordine = IntegerField('Ordine', default=0)

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		super().__init__(*args, **kwargs, submit_label=tasto)
		if not editing:
			self.i_pk_macro.data = db.next_pk('ER_MACRO', 'I_PK_MACRO')
