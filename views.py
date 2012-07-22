from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from models import *
#from flask.ext.mongoengine.wtf import model_form
import json
from flask import session, flash
from flask import g

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
	request_token_params={'scope': ('email', 'manage_friendlists', 'read_friendlists')}
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
		session['facebook_id'] = me.data['id']

		return redirect(next_url)

users.add_url_rule('/login', view_func=LoginView.as_view('login'))
users.add_url_rule('/facebook-login', view_func=FacebookLoginView.as_view('facebook-login'))
users.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))
users.add_url_rule('/facebook-authorized', view_func=FacebookAuthorizedView.as_view('facebook-authorized'))


#------------------------
# api
#------------------------

import requests
#import urllib

def get_friend_ids_from_cluster(cluster):
	friend_ids = []
	for friend in cluster['members']:
		friend_ids.append(friend['i'])
	return friend_ids

class CreateFriendLists(MethodView):
	def get(self):
		momchil_cluster_names = {1: 'Facebook Interns', 2: 'Princeton Entrepreneurship Club', 3: 'High School Friends', 4: 'Bulgarians in Computer Science', 7: 'Fraternity', 8: 'Stanford e-Bootcamp', 10: 'Bulgarians at Princeton', 17: 'MemSQL Team', 20: 'My Family'}
		cluster_names = momchil_cluster_names

		cluster_response = None
		try:
			with open('data/' + session['facebook_id'] + '.json', 'r') as f:
				json_data = f.read()
				cluster_response = json.loads(json_data)
		except:
			print "could not open file"

		#headers = {'content-type': 'application/json'}
		#resp = requests.post('http://localhost:5000/createfriendlists/', data=json.dumps(cluster_names), headers=headers)
		#print resp.text

		return render_template('users/create_lists.html', cluster_names=json.dumps(cluster_names), cluster_response=json.dumps(cluster_response))

	def post(self):
		cluster_names = None
		try:
			cluster_names = json.loads(request.form['cluster_names'])
		except:
			print "could not load cluster names"
			return { "success" : False, "error" : "could not load cluster names" }

		my_cluster_response = None		
		try:
			my_cluster_response = json.loads(request.form['cluster_response'])
		except:
			print "could not load cluster response"
			return { "success" : False, "error" : "could not load cluster response" }


		clusters = my_cluster_response['clusters']
		for key in cluster_names:
			try:
				cluster = clusters[int(key)]
				resp = facebook.post('/friendlists?name=' + str(cluster_names[key]).replace(' ', "%20"))
				try:
					friendlist_id = resp.data['id']
					friend_ids_in_cluster = get_friend_ids_from_cluster(cluster)
					for user_id in friend_ids_in_cluster:
						resp = facebook.post(friendlist_id + "/members/" + user_id)
					print "created group: %s" % str(cluster_names[key])
				except:
					print "failed to create group: %s" % str(cluster_names[key])
					return { "success" : False, "error" : "failed to create group: %s" % str(cluster_names[key]) }
			except:
				print "invalid key for cluster names"
				return { "success" : False, "error" : "invalid key for cluster names" }

		return { "success" : True }

class GenerateFriendListView(MethodView):
	def post(self):
		response = { "success" : False }
		data = None
		try:
			data = request.form
			print data
			try:
				friendlist_name = data.getlist('name')[0]
				print friendlist_name
				friendlist_name = str(friendlist_name).replace(' ', '%20')
				print friendlist_name
				resp = facebook.post('/friendlists?name=' + friendlist_name)
				print friendlist_name
				print resp.data
				try:
					friendlist_id = resp.data['id']
					try:
						members = json.loads(data.getlist('members')[0])
						print members
						for member in members:
						        print member
							resp = facebook.post(friendlist_id + "/members/" + member['i'])
						response = { "success" : True, "friendlist_id": friendlist_id }
					except:
						response = { "success" : False, "error" : "members of friendlist not found" }
				except:
					response = { "success" : False, "error" : "friendlist could not be created" } 
			except:
				response = { "success" : False, "error" : "friendlist name not found" }
		except:
			response = { "success" : False, "error" : "could not load request data" }

                print response
		return json.dumps(response)

class GetClustersView(MethodView):
	def get(self, access_token):
		#print access_token
		url = 'http://api.graphmuse.com:8081/clusters?auth=' + access_token
		r = requests.get(url)
		
		#print r.json
		"""try:
			with open('data/' + session['facebook_id'] + '.json', 'w') as f:
				json_data = json.dumps(r.json)
				f.write(json_data)
		except:
			print "could not write to file"""

		return { "success" : True }

class FacebookApiRequests(MethodView):
	def get(self, string):
		data = facebook.get("/" + string).data
		return json.dumps(data)

users.add_url_rule('/api/<string>/', view_func = FacebookApiRequests.as_view('api'))
users.add_url_rule('/getclusters/<access_token>/', view_func = GetClustersView.as_view('getclusters'))
users.add_url_rule('/createfriendlists/', view_func = CreateFriendLists.as_view('createfriendlists'))
users.add_url_rule('/generatefriendlist/', view_func = GenerateFriendListView.as_view('generatefriendlist'))
