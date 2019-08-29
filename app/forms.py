from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, ValidationError, FieldList, FormField, SelectField
from wtforms.validators import DataRequired
from app.models import Classifier
import pandas as pd


def model_duplicate(form, field):
    name = Classifier.query.filter_by(name=field.data).first()
    if name is not None:
        raise ValidationError("A model by this name already exits!")


def model_duplicate2(form, field):
    name = Classifier.query.filter_by(name=field.data).first()
    if name is None:
        raise ValidationError("A model by this name does not exist!")


def xlsxpars(form, field):
    df = pd.read_excel(field.data, header=[0,1])
    df_headers = df.columns.levels[0].values
    for file_name in df_headers:
        if len(df[file_name].count()) != 4:
            raise ValidationError("Conversation names not unique or the file is not correctly formatted.")
    if len(df.columns.levels[1].values) != 4:
        raise ValidationError("Conversation names not unique or the file is not correctly formatted.")

    if not {'time_start', 'time_end', 'time_diff', 'speaker_id'}.issubset(df.columns.levels[1].values):
        raise ValidationError("Conversation names not unique or the file is not correctly formatted.")

def xlsxpars2(form, field):
    df = pd.read_excel(field.data, header=[0,1])
    if len(df.columns.levels[1].values) != 4:
        raise ValidationError("File does not have the correct formatting.")

    if not {'time_start', 'time_end', 'time_diff', 'speaker_id'}.issubset(df.columns.levels[1].values):
        raise ValidationError("File must have the following sub-heading: "
                              "time_start, time_end, time_diff and speaker_id.")


class Name(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Find!')


class Uploads(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), model_duplicate])
    bad = FileField('Bad audio example file Upload', validators=[DataRequired(), xlsxpars2])
    good = FileField('Good audio example file Upload', validators=[DataRequired(), xlsxpars2])
    submit = SubmitField('Create!')


class Testing(FlaskForm):
    files = FileField('Testing file Upload', validators=[DataRequired(), xlsxpars2])
    submit = SubmitField('Test!')


class Update(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), model_duplicate2])
    files = FileField('New files upload', validators=[DataRequired(), xlsxpars])
    submit = SubmitField('Update!')


class filesType(FlaskForm):
    file_name = StringField('label', render_kw={'readonly': True})
    types = SelectField(choices=([True, 'Good'], [False, 'Bad']))


class Update2(FlaskForm):
    files = FieldList(FormField(filesType))
