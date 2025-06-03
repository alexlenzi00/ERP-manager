from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Gruppo(BaseModel):
	I_PK_GRUPPI: int
	A_DESC_GRUPPI: str
	I_ORDINE_GRUPPI: int = 0

	table = 'ER_GRUPPI'
	pk = ['I_PK_GRUPPI']

class FormGruppi(BaseForm):
	i_pk_gruppi = IntegerField('PK Gruppo', validators=[DataRequired()], render_kw={'readonly': True})
	a_desc_gruppi = StringField('Gruppo', validators=[DataRequired()])
	i_ordine_gruppi = IntegerField('Ordine', default=0)

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		super().__init__(*args, **kwargs, submit_label=tasto)
		if not editing:
			self.i_pk_gruppi.data = db.next_pk('ER_GRUPPI', 'I_PK_GRUPPI')
