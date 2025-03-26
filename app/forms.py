from flask_wtf import FlaskForm
from wtforms.fields import TextField
from wtforms.validators import Required

class TaskForm(FlaskForm):
	label = TextField('label', validators = [Required()])