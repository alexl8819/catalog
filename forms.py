""" Forms """
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Regexp, Length

from flask_wtf import FlaskForm

TITLE_ERROR_MESSAGE = 'Title must be alphanumeric'
DESC_ERROR_MESSAGE = 'Description must be alphanumeric'

TITLE_REGEXP = Regexp(r'^([A-Za-z0-9]+\s?)*$', message=TITLE_ERROR_MESSAGE)
DESC_REGEXP = Regexp(r'^([A-Za-z0-9]+\s?)*$', message=DESC_ERROR_MESSAGE)


class CreateForm(FlaskForm):
    """ Create entry form """
    title = StringField('Title', validators=[DataRequired(),
                                             TITLE_REGEXP,
                                             Length(min=1, max=12)])
    description = StringField('Description', validators=[DESC_REGEXP,
                                                         Length(min=0,
                                                                max=64)])
    category = SelectField('Category', coerce=int,
                           choices=[], validators=[DataRequired()])


class EditForm(FlaskForm):
    """ Edit entry form """
    title = StringField('Title', validators=[DataRequired(),
                                             TITLE_REGEXP,
                                             Length(min=3, max=12)])
    description = StringField('Description', validators=[DESC_REGEXP,
                                                         Length(min=0,
                                                                max=64)])
    category = SelectField('Category', coerce=int,
                           choices=[], validators=[DataRequired()])


class DeleteForm(FlaskForm):
    """ Delete entry form """
    pass
