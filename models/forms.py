from flask_wtf import FlaskForm
from wtforms import SubmitField

class BaseForm(FlaskForm):
	submit = SubmitField('Aggiungi')

	def __init__(self, *args, submit_label=None, **kwargs):
		super().__init__(*args, **kwargs)
		if submit_label:
			self.submit.label.text = submit_label
