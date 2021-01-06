from flask_wtf import FlaskForm
from wtforms import DateField, TimeField, StringField, SubmitField, FloatField
from wtforms.validators import DataRequired,Length

class MovementForm(FlaskForm): #hereda de FlaskForm
    from_currency = StringField('from_currency', validators=[DataRequired(), Length(min=3, message="Debe de tener al menos 3 caracteres")])
    q1 = FloatField('Cantidad', validators=[DataRequired()])
    to_currency = StringField('from_currency', validators=[DataRequired(), Length(min=3, message="Debe de tener al menos 3 caracteres")])
    submit = SubmitField('¡Compra ya!')
    
