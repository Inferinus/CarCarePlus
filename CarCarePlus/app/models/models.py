from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

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
    vin = db.Column(db.String(50), unique=True, nullable=False)


    # Keep only one foreign key that links a Car to a User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_cars_user_id'), nullable=False)

    # The relationship is now set with foreign_keys argument to avoid ambiguity
    owner = db.relationship('User', backref=db.backref('cars', lazy=True), foreign_keys=[user_id])


    def calculate_age(self):
        current_year = datetime.now().year
        return current_year - self.year

    def __repr__(self):
        return f'<Car {self.make} {self.model} ({self.year})>'

class MaintenanceLog(db.Model):
    __tablename__ = 'maintenance_logs'

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id', name='fk_maintenance_logs_car_id'), nullable=False)
    car = db.relationship('Car', backref=db.backref('maintenance_logs', lazy=True))
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

def init_app(app):
    # Call this in your app to initialize the SQLAlchemy with the app's configuration
    db.init_app(app)
