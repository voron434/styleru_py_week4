from flask import Flask
import os

app = Flask(__name__)
app.config.from_object('config')
app.config.update(CSRF_ENABLED = os.environ['CSRF_ENABLED'])
app.config.update(SECRET_KEY = os.environ['SECRET_KEY'])
app.config.update(CLIENT_ID = os.environ['CLIENT_ID'])
app.config.update(CLIENT_SECRET = os.environ['CLIENT_SECRET'])
from app import views
