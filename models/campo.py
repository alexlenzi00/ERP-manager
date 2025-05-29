from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Campo(BaseModel):
	I_PK_CAMPO: int | None
	I_FK_TABELLA: int
	A_NOME_CAMPO: str
	A_DESC_CAMPO: str
	A_TIPO_CAMPO: str
	A_NOTE_CAMPO: str | None = None
	A_ALIAS: str = ''
	A_FLAG_GROUP: str = 'N'
	I_ORDINE: int = 0
	A_STRQUERY: str | None = None
	I_FK_MACROSHOW: int | None = None
	I_FK_GRUPPO: int | None = None

	table = "ER_CAMPI"
	pk = ["I_PK_CAMPO"]
	cols = ("I_PK_CAMPO", "I_FK_TABELLA", "A_NOME_CAMPO", "A_DESC_CAMPO",
			"A_TIPO_CAMPO", "A_NOTE_CAMPO", "A_ALIAS", "A_FLAG_GROUP",
			"I_ORDINE", "A_STRQUERY", "I_FK_MACROSHOW", "I_FK_GRUPPO")

class FormCampi(BaseForm):
	i_pk_campo = IntegerField("PK Campo", validators=[DataRequired()])
	i_fk_tabella = SelectField("Tabella", coerce=int, validators=[DataRequired()])
	a_nome_campo = StringField("Nome completo colonna", validators=[DataRequired()])
	a_desc_campo = StringField("Descrizione", validators=[DataRequired()])
	a_tipo_campo = StringField("Tipo", validators=[DataRequired()])
	a_alias = StringField("Alias", validators=[DataRequired()])
	a_flag_group = SelectField("Si può fare la GROUP BY su questo campo?", coerce=str)
	i_ordine = IntegerField("Ordine", default=0)
	i_fk_macros = SelectField("Macro Show", coerce=int, validators=[Optional()])
	i_fk_group = SelectField("Gruppo", coerce=int, validators=[Optional()])

	def __init__(self, db, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.i_pk_campo.data = db.next_pk("ER_CAMPI", "I_PK_CAMPO")
		self.a_flag_group.choices = [("N", "No"), ("S", "Si")]
		self.i_fk_tabella.choices = [(t["I_PK_TABELLA"], t["A_NOME_TABELLA"]) for t in db.fetchall("SELECT I_PK_TABELLA, A_NOME_TABELLA FROM ER_TABELLE ORDER BY 2")]
		self.i_fk_macros.choices = [(-1, ". . .")] + [(m["I_PK_MACRO"], f'{m["I_PK_MACRO"]} - {m["A_DESC_MACRO"]}') for m in db.fetchall("SELECT I_PK_MACRO, A_DESC_MACRO FROM ER_MACRO ORDER BY 1")]
		self.i_fk_group.choices = [(-1, ". . .")] + [(g["I_PK_GRUPPI"], g["A_DESC_GRUPPI"]) for g in db.fetchall("SELECT I_PK_GRUPPI,A_DESC_GRUPPI FROM ER_GRUPPI ORDER BY 2")]
