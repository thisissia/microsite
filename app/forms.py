from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, ValidationError, FieldList, FormField, SelectField
from wtforms.validators import DataRequired
from app.models import Classifier


def model_duplicate(form, field):
    name = Classifier.query.filter_by(name=field.data).first()
    if name is not None:
        raise ValidationError("A model by this name already exits!")


def model_duplicate2(form, field):
    name = Classifier.query.filter_by(name=field.data).first()
    if name is None:
        raise ValidationError("A model by this name does not exist!")

class Name(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Find!')


class Uploads(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), model_duplicate])
    bad = FileField('Bad audio example file Upload', validators=[DataRequired()])
    good = FileField('Good audio example file Upload', validators=[DataRequired()])
    submit = SubmitField('Create!')


class Testing(FlaskForm):
    files = FileField('Testing file Upload', validators=[DataRequired()])
    submit = SubmitField('Test!')


class Update(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), model_duplicate2])
    files = FileField('New files upload', validators=[DataRequired()])
    submit = SubmitField('Update!')


class filesType(FlaskForm):
    file_name = StringField('label', render_kw={'readonly': True})
    types = SelectField(choices=([True, 'Good'], [False, 'Bad']))


class Update2(FlaskForm):
    files = FieldList(FormField(filesType))
