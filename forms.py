from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

# Search form
class queryForm(FlaskForm):
    searched_title = StringField("Searched_Title", validators=[DataRequired()])
    searched_artist = StringField("Searched_Artist", validators=[DataRequired()])
    searched_year = StringField("Searched_Year", validators=[DataRequired()])
    submit = SubmitField("Submit")
