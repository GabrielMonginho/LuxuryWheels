from wtforms.validators import Length, Email, EqualTo, DataRequired, ValidationError
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField
from wtforms.fields import DateField, DateTimeField
from flask_wtf import FlaskForm
from website.models import User

class RegisterForm (FlaskForm):
    
    def validate_email_address(self, email_address_to_check):
        email_address= User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError("Email address already exists! Please try a different email address")

    first_name= StringField(label='First Name:', validators=[Length(min=2, max=30), DataRequired()])
    surname= StringField(label='Surname:', validators=[Length(min=2, max=30), DataRequired()])
    email_address=StringField(label='Email Address:', validators = [Email(), DataRequired()])
    password1 = PasswordField(label='Password', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    gender = SelectField(label='Gender', choices=[( 'Male'), ('Female'), ( 'Other')], validators=[DataRequired()])
    phone_code = SelectField(label='Phone Code', choices=[('USA (+1)'),('Portugal (+351)'), ('Brasil (+55)'),('Spain (+34)'),('Germany (+49)')], validators=[DataRequired()])
    phone_number= StringField(label='Phone number', validators=[Length(min=2, max=30), DataRequired()])
    birth= DateField('Birthday', format='%Y-%m-%d')
    category = SelectField(label='Choose your limit budget', choices=[('Gold (600$)'),('Silver (250$)'), ( 'Economic (50$)')], validators=[DataRequired()])
    driver_license= StringField(label='Driver License', validators=[Length(min=5,max=20), DataRequired()])
    id_passport= StringField(label='ID/Passport', validators=[Length(min=5,max=20), DataRequired()])
        
    submit = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    email= StringField(label='Email:', validators=[DataRequired()])
    password= PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Log in')

class OrderTimeForm(FlaskForm):
    start = DateField('Check-in', format='%Y-%m-%d')
    finish= DateField('Check-out', format='%Y-%m-%d')
    submit=SubmitField(label='Add to cart 🛒')

class ProductFilterForm(FlaskForm):
    brand = SelectField(label='Brand', choices=[('Select brand'),('Mercedes'),('Citroen'), ('Porsche'),('Audi'),('Ford'),('Opel'),('Volkswagen'),('Honda'),('Yamaha'),('Bmw'),('Seat'),('Smart'),('Toyota'),('Peugeot'),('Skoda'), ('Renault')], validators=[DataRequired()])
    category = SelectField(label='Category', choices=[('Select category'),('Gold(600$)'),('Silver(250$)'), ('Economic(50$)')], validators=[DataRequired()])
    type = SelectField(label='Type', choices=[('Select type'),('Car'),('Suv'), ('Motorcycle')], validators=[DataRequired()])
    daily_price = SelectField(label='Daily price', choices=[('Select daily price'),('8'),('15'), ('29')], validators=[DataRequired()])
    passengers = SelectField(label='Passengers', choices=[('Select number of passengers'),('2'), ('4'), ('5')], validators=[DataRequired()])
    doors = SelectField(label='Doors', choices=[('How many doors?'),('Yes'),('No')], validators=[DataRequired()])
    AC = SelectField(label='AC', choices=[('Need AC?'),('Yes'),('No')], validators=[DataRequired()])
    baggage = SelectField(label='Baggage', choices=[('Need baggage?'),('Yes'),('No')], validators=[DataRequired()])
    doors = SelectField(label='Doors', choices=[('Select number of doors'),('2'), ('4'), ('5')], validators=[DataRequired()])
    fuel = SelectField(label='Fuel', choices=[('Select fuel'),('Gasoline'), ('Diesel'), ('Eletric'),('Hybrid'),('Natural Gas')], validators=[DataRequired()])
    
class PaymentForm(FlaskForm):
    card_type= SelectField(label='Card type', choices=[('Visa'),('Mastercard'),('Paypal'), ('MB Way')], validators=[DataRequired()])
