from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Gruppo(BaseModel):
	I_PK_GRUPPI: int
	A_NOME_GRUPPI: str
	I_ORDINE_GRUPPI: int = 0

	table = "ER_GRUPPI"
	pk = ["I_PK_GRUPPI"]
	cols = ("I_PK_GRUPPI", "A_NOME_GRUPPI", "I_ORDINE_GRUPPI")

class FormGruppi(BaseForm):
	i_pk_group = IntegerField("PK Gruppo", validators=[DataRequired()])
	a_desc_group= StringField("Descrizione", validators=[DataRequired()])
	i_ordine = IntegerField("Ordine", default=0)

	def __init__(self, db,*a,**kw):
		super().__init__(*a,**kw)
		self.i_pk_group.data = db.next_pk("ER_GRUPPI", "I_PK_GRUPPI")
