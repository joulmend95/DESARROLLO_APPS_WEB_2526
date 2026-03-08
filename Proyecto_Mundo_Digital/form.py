"""
Módulo para formularios de la aplicación
Validación y procesamiento de datos de formularios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class ProductoForm(FlaskForm):
    """
    Formulario para añadir/editar productos
    """
    nombre = StringField('Nombre del Producto', 
                        validators=[DataRequired(), Length(min=2, max=100)])
    cantidad = IntegerField('Cantidad', 
                          validators=[DataRequired(), NumberRange(min=0)])
    precio = FloatField('Precio', 
                       validators=[DataRequired(), NumberRange(min=0)])
    categoria = SelectField('Categoría', 
                          choices=[
                              ('Computadoras', 'Computadoras'),
                              ('Periféricos', 'Periféricos'),
                              ('Audio', 'Audio'),
                              ('Monitores', 'Monitores'),
                              ('Software', 'Software'),
                              ('Otros', 'Otros')
                          ],
                          validators=[DataRequired()])
    submit = SubmitField('Guardar')
