from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from os import path

db=SQLAlchemy()
login_manager= LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

bcrypt=Bcrypt()

class User(db.Model, UserMixin):
    __tablename__='Users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    surname = db.Column(db.String(30), nullable=False)
    email_address= db.Column(db.String(50), unique=True, nullable=False)
    password_hash=db.Column(db.String(60),nullable=False)
    gender=db.Column(db.String(30), nullable=False)
    phone_code=db.Column(db.String(20),nullable=False)
    phone_number=db.Column(db.String(25), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    driver_license=db.Column(db.String(25), nullable=False, unique=True)
    id_passport= db.Column(db.String(25), nullable=False, unique=True)
    category=db.Column(db.String(15),nullable=False)
    vehicle=db.relationship('Vehicle', backref='owned_user', lazy=True)
   
    def __repr__(self):
        return f'User {self.first_name, self.surname}'
    
   
        
    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
    
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
    
class Vehicle(db.Model):
    __tablename__='Vehicles'
    id = db.Column(db.Integer, primary_key=True)
    item_name= db.Column(db.String(30), nullable=False)
    item_type= db.Column(db.String(10), nullable=False)
    item_model= db.Column(db.String(30), nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    daily_price = db.Column(db.Integer, nullable = False)
    item_barcode= db.Column(db.String(12), nullable=False, unique=True)
    passengers= db.Column(db.Integer, nullable=False)
    doors=db.Column (db.Integer, nullable=False)
    AC=db.Column(db.String(5), nullable=False)
    fuel=db.Column(db.String(15), nullable=False)
    baggage=db.Column(db.String(5), nullable=False)
    gear=db.Column(db.String(20), nullable=False)
    power=db.Column(db.Integer, nullable=False)
    co2=db.Column(db.Integer, nullable=False)
    image=db.Column(db.String(30), nullable=False)
    last_review=db.Column(db.Date, nullable=False)
    next_review=db.Column(db.Date, nullable=False)
    inspection=db.Column(db.Date, nullable=False)
    desc=db.Column(db.String(1000))
    owner_id = db.Column(db.Integer(), db.ForeignKey('Users.id'))

    def __repr__(self):
        return f'Vehicle {self.item_name}'
    
    

    

    def to_dict(self):
        return {
            "id": self.id,
            "item_name": self.item_name,
            "item_type":self.item_type,
            "item_model":self.item_model,
            "item_price":self.item_price,
            "daily_price":self.daily_price,
            "item_barcode":self.item_barcode,
            "passengers":self.passengers,
            "doors":self.doors,
            "AC":self.AC,
            "fuel":self.fuel,
            "baggage":self.baggage,
            "gear":self.gear,
            "power":self.power,
            "co2":self.co2,
            "gear":self.gear,
            "image":self.image,
            "desc":self.desc,
            "owner_id":self.owner_id,
            }
    


class Temporary_order(db.Model):
    __tablename__='~Temporary orders'
    id= db.Column(db.Integer, primary_key=True)
    product_id=db.Column(db.Integer, db.ForeignKey('Vehicles.id'))
    owner_id=db.Column(db.Integer, db.ForeignKey('Users.id'))
    days=db.Column(db.Integer, nullable=False)
    start=db.Column(db.DateTime, nullable=False)
    finish=db.Column(db.DateTime, nullable=False)
    daily_price=db.Column(db.Integer, nullable=False)
    order_price=db.Column(db.Integer, db.ForeignKey('Vehicles.item_price'))
    price_exchange= db.Column(db.Integer, nullable=True)

    def total_price(self, start, finish, daily_price):
        self.order_price=(self.finish-self.start)*self.daily_price
        return self.order_price
    
    def to_dict(self):
            return {
                "id": self.id,
                "product_id": self.product_id,
                "owner_id":self.owner_id,
                "days":self.days,
                "start":self.start,
                "finish":self.finish,
                "daily_price":self.daily_price,
                "order_price":self.order_price,
                }
    
    
class Order(db.Model):
    __tablename__='Orders'
    id= db.Column(db.Integer, primary_key=True)
    product_id=db.Column(db.Integer, db.ForeignKey('Vehicles.id'))
    owner_id=db.Column(db.Integer, db.ForeignKey('Users.id'))
    days=db.Column(db.Integer, nullable=False)
    start=db.Column(db.DateTime, nullable=False)
    finish=db.Column(db.DateTime, nullable=False)
    daily_price=db.Column(db.Integer, nullable=False)
    order_price=db.Column(db.Integer, db.ForeignKey('Vehicles.item_price'))
    price_exchange= db.Column(db.Integer, nullable=True)
    state= db.Column(db.String(10), nullable=True)
    
    def total_price(self, start, finish, daily_price):
        self.order_price=(self.finish-self.start)*self.daily_price
        return self.order_price
    
    def to_dict(self):
            return {
                "id": self.id,
                "product_id": self.product_id,
                "owner_id":self.owner_id,
                "days":self.days,
                "start":self.start,
                "finish":self.finish,
                "daily_price":self.daily_price,
                "order_price":self.order_price,
                }
    



class Payment(db.Model):
    __tablename__='Payments'
    id=db.Column(db.Integer, primary_key=True)
    amount=db.Column(db.Integer, nullable=False)
    card_type=db.Column(db.String, nullable=False)
    id_user=db.Column(db.Integer, db.ForeignKey('Users.id'))
    id_order=db.Column(db.Integer, db.ForeignKey('Orders.id'))
