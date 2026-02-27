# exercise1/__init__.py
from flask import Blueprint

# Define the blueprint
ex1_bp = Blueprint('ex1', __name__, template_folder='templates')

# Import the routes so they are registered
from . import routes