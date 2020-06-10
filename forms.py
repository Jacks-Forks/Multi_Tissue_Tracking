from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (FileField, IntegerField, RadioField, SelectField,
                     SubmitField, TextAreaField, TextField, ValidationError,
                     validators)
from wtforms.fields.html5 import DateField


class upload_file_form(FlaskForm):
    date_recorded = DateField('Date Recorded', [validators.Required()])
    num_tissues = IntegerField('Number Of Feilds')
    bio_reactor = SelectField('Reactor', choices=[('a', 'a'), ('b', 'b')])
    file = FileField('Upload a File', [validators.Required()])
    submit = SubmitField('Upload')
