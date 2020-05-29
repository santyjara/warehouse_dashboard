from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField, FileField, SelectField
from wtforms.validators import DataRequired


class loginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class upload_Form(FlaskForm):
    file1 = FileField('Ingrese la ruta del archivo No. 1',validators=[DataRequired()])
    file2 = FileField('Ingrese la ruta del archivo No. 2')
    file3 = FileField('Ingrese la ruta del archivo No. 3')
    file4 = FileField('Ingrese la ruta del archivo No. 4')
    file5 = FileField('Ingrese la ruta del archivo No. 5')

    upload = SubmitField('Upload')


