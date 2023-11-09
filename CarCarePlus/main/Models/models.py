from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    cars = db.relationship('Car', backref='owner', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Car(db.Model):
    __tablename__ = 'cars'

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    mileage = db.Column(db.Integer, nullable=True)
    vin = db.Column(db.String(50), nullable=True) #Note: 'unique=True' Was removed and nullable was set as True for development purposes, to be re-added and to be set as False for production.
    #manufacturer = db.Column(db.String(50), nullable=True)
    #engine = db.Column(db.String(50), nullable=True)
    #trim = db.Column(db.String(50), nullable=True)
    #transmission = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Car {self.make} {self.model} ({self.year})>'


class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    service_performed = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cost = db.Column(db.Float, nullable=True)
    comments = db.Column(db.String(500))

    def format_date(self):
        return self.date.strftime('%Y-%m-%d')

    def time_since_maintenance(self):
        return (datetime.now() - self.date).days

    def __repr__(self):
        return f'<MaintenanceLog {self.service_performed} on {self.format_date()}>'


class VehicleRepair(db.Model):
    __tablename__ = 'vehicle_repairs'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    dtc_code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    repair_urgency = db.Column(db.Integer, nullable=True)
    repair_difficulty = db.Column(db.Integer, nullable=True)
    parts_needed = db.Column(db.Text, nullable=True)
    labor_hours = db.Column(db.Float, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    date_diagnosed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<VehicleRepair {self.dtc_code} for Car ID {self.car_id}>'
