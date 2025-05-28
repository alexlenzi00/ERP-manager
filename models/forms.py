from flask_wtf import FlaskForm
from wtforms import SubmitField

class BaseForm(FlaskForm):
	submit = SubmitField("Aggiungi")

	def to_dict(self):
		return {k: v.data for k, v in self._fields.items() if k != "submit"}
