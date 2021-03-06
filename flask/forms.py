import models
from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, FieldList, FileField, Form,
                     FormField, HiddenField, IntegerField, SelectField,
                     SelectMultipleField, StringField, SubmitField, validators,
                     widgets)
from wtforms.fields.html5 import DateField


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class Tissue_Samples(Form):
    post_in_use = BooleanField(
        'Check If Post In Use')
    tissue_num = StringField('Tissue Number')
    type_of_tissue = StringField('Type of Tissue')


class upload_to_b_form(FlaskForm):
    date_recorded = DateField('Date Recorded', [validators.Required()])
    post = FieldList(FormField(Tissue_Samples), min_entries=6)
    frequency = DecimalField('Enter the Frequency')
    bio_reactor = SelectField('Select Bio')
    #bio_reactor_num = IntegerField('Enter Bio Reactor Number')
    experiment_num = StringField('Enter Experiment number')
    file = FileField('Upload a File', [validators.Required()])
    submit = SubmitField('Upload')


class upload_experiment(FlaskForm):
    file = FileField('Upload a File', [validators.Required()])
    submit = SubmitField('Upload')


class PickVid(FlaskForm):
    experiment = SelectField('Experiment', id='select_experiment')
    date = SelectField('Date', id='select_date')
    vids = SelectField('Vids', id='select_vids')
    submit = SubmitField('Select Video')


class calibrationFactor(FlaskForm):
    # REVIEW: does this even get used
    cal_factor = DecimalField("Calibration Factor")
    submit = SubmitField('Submit')


class Post(Form):
    left_tissue_height = DecimalField('Enter left tissue height')
    left_post_height = DecimalField('Enter left post height')
    right_tissue_height = DecimalField('Enter right tissue height')
    right_post_height = DecimalField('Enter right post height')


class addBio(FlaskForm):
    bio_number = IntegerField('Enter Bio Reactor Number')
    date_added = DateField('Date Added', [validators.Required()])
    posts = FieldList(FormField(Post), min_entries=6)
    submit = SubmitField('Submit')
