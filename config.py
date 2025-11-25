class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:hetaT-601@localhost:3306/mechanic_shop'
    DEBUG = True
    
class TestingConfig:
    pass

class ProductionConfig:
    pass