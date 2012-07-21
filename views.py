from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from models import *
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

#------------------------
# login
#------------------------

from flaskext.oauth import OAuth
from flask import session, flash

FACEBOOK_APP_ID = '498464373503828'
FACEBOOK_APP_SECRET = 'f4e24d77158bd708f3b6fa0d671a5102'

oauth = OAuth()
facebook = oauth.remote_app('facebook',
	base_url='https://graph.facebook.com/',
	request_token_url=None,
	access_token_url='/oauth/access_token',
	authorize_url='https://www.facebook.com/dialog/oauth',
	consumer_key=FACEBOOK_APP_ID,
	consumer_secret=FACEBOOK_APP_SECRET,
	request_token_params={'scope': ('email', 'manage_friendlists')}
)

@facebook.tokengetter
def get_facebook_token():
	return session.get('facebook_token')

class LoginView(MethodView):
	def get(self):
		return render_template('users/login.html')

def pop_all_login_sessions():
	session.pop('logged_in', None)
	session.pop('facebook_token', None)
	session.pop('facebook_id', None)

class FacebookLoginView(MethodView):
	def get(self):
		return facebook.authorize(callback=url_for('users.facebook-authorized',
			next=request.args.get('next'),
			_external=True))

class LogoutView(MethodView):
	def get(self):
		pop_all_login_sessions()
		return redirect(url_for('users.index'))

class FacebookAuthorizedView(MethodView):
	@facebook.authorized_handler
	def get(resp, self):
		next_url = request.args.get('next') or url_for('users.index')
		if resp is None or 'access_token' not in resp:
			flash(u'You could not be signed in.')
			return redirect(next_url)

		session['logged_in'] = True
		session['facebook_token'] = (resp['access_token'], '')

		me = facebook.get('/me')
		print me.data
		return redirect(next_url)

users.add_url_rule('/login', view_func=LoginView.as_view('login'))
users.add_url_rule('/facebook-login', view_func=FacebookLoginView.as_view('facebook-login'))
users.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
users.add_url_rule('/facebook-authorized', view_func=FacebookAuthorizedView.as_view('facebook-authorized'))






