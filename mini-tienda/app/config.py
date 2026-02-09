import os 
SECRET_KEY = 'my-secret-key'
PWD = os.path.abspath(os.curdir)
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}/dbase.db'.format(PWD)
SQLALCHEMY_DATABASE_MODIFICATIONS = False