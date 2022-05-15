from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField
# from wtforms_components import DateRange
from wtforms.validators import InputRequired, DataRequired, Length, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed
# from datetime import datetime, date

class UploadForm(FlaskForm):
    audioFile = FileField('AudioFile', validators=[
        FileRequired(),
        FileAllowed(['ogg', 'mp4', 'webm', 'mpeg','mp3','wav','Audio or Video Files Only'])
    ])



class SignUpForm(FlaskForm):
    fullname= StringField('Full Name',
    validators=[InputRequired(),
    Length(max=40)])

    username = StringField('Username', 
    validators=[InputRequired()])

    email = StringField(
        'E-mail',
        validators=[
            Email(message=('Not a valid email address.')),
            DataRequired()
        ]
    )

    dateofbirth = DateField(
            'Date of Birth',
            validators=[DataRequired()])
    
    password = PasswordField('Password',
    validators=[InputRequired()])

    password_reenter = PasswordField('Re-enter Password',
    validators=[InputRequired()])
    
class LoginForm(FlaskForm):
    username = StringField('Username', 
    validators=[InputRequired()])

    password = PasswordField('Password',
    validators=[InputRequired()])
