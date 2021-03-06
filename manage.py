# Set the path
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask.ext.script import Manager, Server
from __init__ import app

manager = Manager(app)

port = int(os.environ.get('PORT', 5000))


#FACEBOOK_APP_ID = '340867512667352'
#FACEBOOK_APP_SECRET = 'd595097b376fb5fba5ea3ea3d8a72ddf'

#if port == 5000:

	#FACEBOOK_APP_ID = '412356285476795'
	#FACEBOOK_APP_SECRET = '766f8133b12b913103707875fa2078b6'
#	FACEBOOK_APP_ID = '498464373503828'
#	FACEBOOK_APP_SECRET = 'f4e24d77158bd708f3b6fa0d671a5102'

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger = False,
    use_reloader = True,
    port = port,
    host = '0.0.0.0')
)

if __name__ == "__main__":
    manager.run()