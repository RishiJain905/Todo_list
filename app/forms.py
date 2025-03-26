from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import DataRequired
from wtforms.fields import StringField
class TaskForm(FlaskForm):
	label = StringField('label', validators=[DataRequired()])

