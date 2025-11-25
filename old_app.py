from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Date, ForeignKey, Table, Column
from datetime import date
from typing import List

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:<YOUR MYSQL PASSWORD>@localhost/<YOUR DATABASE>'



# Instantiate SQLAlchemy database
db = SQLAlchemy(model_class=Base)

# Adding our db extension to our app
db.init_app(app)


    
    
# Create the tables
with app.app_context():
    db.create_all()
    
app.run(debug=True)