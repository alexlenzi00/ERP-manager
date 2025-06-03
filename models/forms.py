from flask_wtf import FlaskForm
from wtforms import SubmitField

class BaseForm(FlaskForm):
	submit = SubmitField('Aggiungi')

	def __init__(self, submit_label=None):
		super().__init__()
		if submit_label:
			self.submit.label.text = submit_label
