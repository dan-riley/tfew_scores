import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    UPLOAD_FOLDER = os.path.join(basedir, 'upload')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
