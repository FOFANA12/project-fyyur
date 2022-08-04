import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@127.0.0.1:5432/projectfyyur'
SQLALCHEMY_DATABASE_URI = 'postgres://hcorblbbzelurs:3afd641952c0a6f20e604cfab6924f7b2fd40d6b7c2c7f1d8ee136095d842eb7@ec2-54-85-56-210.compute-1.amazonaws.com:5432/dd70in5fgskkal'
SQLALCHEMY_TRACK_MODIFICATIONS = False