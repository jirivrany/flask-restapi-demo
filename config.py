import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.getenv("SECRET_KEY", "lkdajc049dfnLSKFJ38FOIJEJFPA48FU40U8JLJSAKJDSLAKJklk")
    JWT_SECRET = os.getenv("JWT_SECRET", "sak3f4oufpfojprdovasporgvkjpojgvpoavjproksada3#$$SSK")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "")

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///demo.db'