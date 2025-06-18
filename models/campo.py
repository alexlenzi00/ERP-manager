from wtforms import StringField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional
from .forms import BaseForm
from .models import BaseModel
from dataclasses import dataclass

@dataclass
class Campo(BaseModel):
	I_PK_CAMPO: int
	I_FK_TABELLA: int
	A_NOME_CAMPO: str
	A_DESC_CAMPO: str
	A_TIPO_CAMPO: str
	A_NOTE_CAMPO: str = ''
	A_ALIAS: str = ''
	A_FLAG_GROUP: str = 'N'
	I_ORDINE: int = 0
	A_STRQUERY: str | None = None
	I_FK_MACROSHOW: int = -1
	I_FK_GRUPPO: int | None = None

	table = 'ER_CAMPI'
	pk = ['I_PK_CAMPO']

class FormCampi(BaseForm):
	i_pk_campo = IntegerField('PK Campo', validators=[DataRequired()], render_kw={'readonly': True})
	i_fk_tabella = SelectField('Tabella', coerce=int, validators=[DataRequired()])
	a_nome_campo = StringField('Nome completo colonna', validators=[DataRequired()])
	a_desc_campo = StringField('Descrizione', validators=[DataRequired()])
	a_tipo_campo = SelectField('Tipo', coerce=str, validators=[DataRequired()])
	a_note_campo = StringField('Note', validators=[Optional()])
	a_alias = StringField('Alias', validators=[DataRequired()])
	a_flag_group = SelectField('Si può fare la GROUP BY su questo campo?', coerce=str)
	i_ordine = IntegerField('Ordine', default=0)
	a_strquery = StringField('Query', validators=[Optional()], render_kw={'placeholder': 'Query SQL per il calcolo del campo'})
	i_fk_macroshow = SelectField('Macro', coerce=int, validators=[Optional()])
	i_fk_gruppo = SelectField('Gruppo', coerce=int, validators=[Optional()])

	def __init__(self, db, editing=False, tasto=None, *args, **kwargs):
		super().__init__(*args, **kwargs, submit_label=tasto)
		self.i_fk_tabella.choices = [(t['I_PK_TABELLA'], t['A_NOME_TABELLA']) for t in db.fetchall('SELECT I_PK_TABELLA, A_NOME_TABELLA FROM ER_TABELLE ORDER BY 2')]
		self.a_tipo_campo.choices = [(v, f'{k} ({v})') for k, v in db.config['costanti']['tipi'].items()]
		self.a_flag_group.choices = [('N', 'No'), ('S', 'Si')]
		self.i_fk_macroshow.choices = [(-1, '. . .')] + [(m['I_PK_MACRO'], f'{m['I_PK_MACRO']} - {m['A_DESC_MACRO']}') for m in db.fetchall('SELECT I_PK_MACRO, A_DESC_MACRO FROM ER_MACRO ORDER BY 1')]
		self.i_fk_gruppo.choices = [(-1, '. . .')] + [(g['I_PK_GRUPPI'], f'{g['I_PK_GRUPPI']} - {g['A_DESC_GRUPPI']}') for g in db.fetchall('SELECT I_PK_GRUPPI,A_DESC_GRUPPI FROM ER_GRUPPI ORDER BY 1')]
		if not editing:
			self.i_pk_campo.data = db.next_pk('ER_CAMPI', 'I_PK_CAMPO')
