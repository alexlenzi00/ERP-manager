from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SelectMultipleField, FloatField, RadioField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional

class BaseForm(FlaskForm):
	submit = SubmitField("Aggiungi")

	def to_dict(self):
		return {k: v.data for k, v in self._fields.items() if k != "submit"}










