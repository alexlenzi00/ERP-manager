from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Macro(BaseModel):
	I_PK_MACRO: int
	A_DESC_MACRO: str
	I_ORDINE: int = 0

	table = "ER_MACRO"
	pk = "I_PK_MACRO"
	cols = ("I_PK_MACRO", "A_NOME_MACRO", "I_ORDINE")

	@classmethod
	def daForm(cls, form) -> "Macro":
		data = {c: getattr(form, c).data for c in cls.cols if hasattr(form, c)}
		return cls(**data)

class FormMacro(BaseForm):
	i_pk_macro = IntegerField("PK Macro", validators=[DataRequired()])
	a_nome_macro = StringField("Nome Macro", validators=[DataRequired()])
	i_ordine = IntegerField("Ordine", default=0)

	def __init__(self, db,*a,**kw):
		super().__init__(*a,**kw)
		self.i_pk_macro.data = db.next_pk("ER_MACRO", "I_PK_MACRO")
