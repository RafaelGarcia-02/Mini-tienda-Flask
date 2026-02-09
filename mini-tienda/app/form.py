# Define tus formularios aquí usando Flask-WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, SelectField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

class formArticulo(FlaskForm):
    nombre=StringField('Nombre:',validators=[DataRequired("Tienes que introducir un nombre")])
    precio = DecimalField('Precio:',default=0, validators=[DataRequired("Tienes que introducir un precio")])
    iva = IntegerField('IVA:',default=21, validators=[DataRequired("Tienes que introducir un IVA")])
    descripcion = TextAreaField('Descripción:')
    imagen = FileField('Selecciona imagen:')
    stock = IntegerField('Stock:',default=1, validators=[DataRequired("Tienes que introducir un stock")])
    categoria_id = SelectField('Categoria:', coerce=int, validators=[DataRequired("Tienes que seleccionar una categoria")])
    submit = SubmitField('Guardar')

class formCategoria(FlaskForm):
    nombre=StringField('Nombre:',validators=[DataRequired("Tienes que introducir un nombre")])
    submit = SubmitField('Guardar')

class formSINO(FlaskForm):
    si = SubmitField('Si')
    no = SubmitField('No')

class loginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class formUsuario(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class formChangePassword(FlaskForm):
    password = StringField('New Password', validators=[DataRequired()])
    submit = SubmitField('Change Password')

from wtforms import HiddenField
from wtforms.validators import NumberRange
class formCarrito(FlaskForm):
    id = HiddenField()
    cantidad = IntegerField('Cantidad',default=1,validators=[NumberRange(min=1,message="Debe ser un numero positivo mayor a 0"),DataRequired("Tienes que introducir dato")])
    submit= SubmitField('Aceptar')