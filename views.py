from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from greylocku.models import *
from flask.ext.mongoengine.wtf import model_form
import json

#------------------------
# users
#------------------------

users = Blueprint('users', __name__, template_folder='templates')

class HomeView(MethodView):
    def get(self):
        return render_template('index.html')

users.add_url_rule('/', view_func=HomeView.as_view('index'))



