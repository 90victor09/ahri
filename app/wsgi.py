"""wsgi script to run the old-sso-converter app."""
# import os

from .app import app

application = app
