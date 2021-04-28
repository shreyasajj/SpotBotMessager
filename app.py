import os
from datetime import datetime
from time import sleep

import spotipy
from flask import Flask, request, render_template, redirect
from spotipy.oauth2 import SpotifyOAuth


from api import api
import config


# app = Flask(__name__)


def logging(log, contact):
    f = open("Logging.txt", "a+")
    f.write(str(datetime.now().strftime("%b-%d-%Y %X")) + " - " + contact + " - " + log + "\n")
    f.close()


#


def create_app():
    print(f'Starting app in {config.APP_ENV} environment')
    flask_app = Flask(__name__)
    flask_app.config.from_object('config')
    api.init_app(flask_app)

    @flask_app.route('/', methods=['GET'])
    def index():
        print(request.host_url)
        print(str(request.is_secure))
        return render_template("index.html")

    @flask_app.route('/login', methods=['GET'])
    def spotifyLogin():

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path='.cache')
        auth_manager = SpotifyOAuth(client_id=os.environ["CLIENT_ID"],
                                    client_secret=os.environ["CLIENT_SECRET"],
                                    redirect_uri=request.host_url + "login",
                                    scope="user-modify-playback-state "
                                          "user-read-playback-state "
                                          "user-read-recently-played")
        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            auth_manager.get_access_token(request.args.get("code"))
            logging("Logged In", "System")
            print("Need to login Redirecting")
            return redirect('/')
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            print("Need to login Redirecting")
            print("Redirect URL is: " + request.host_url + "login")
            logging("REDIRECT URL is: " + request.host_url + "login", "System")
            logging("Need to login Redirecting", "System")
            return redirect(auth_url)
        logging("Already Login Passing on", "System")
        return redirect('/')

    @flask_app.route('/stream', methods=['GET'])
    def stream():
        def generate():

            fname = "Logging.txt"
            while not os.path.isfile(fname):
                sleep(1)
            with open(fname) as f:
                while True:
                    yield f.read()
                    while not os.path.isfile(fname):
                        sleep(1)
                    sleep(1)

        return flask_app.response_class(generate(), mimetype='text/plain')

    return flask_app


if __name__ == '__main__':

    if "CLIENT_ID" in os.environ and "CLIENT_SECRET" in os.environ:
        app = create_app()
        app.run()
    else:
        print("Please Provide \'CLIENT_ID\' and \'CLIENT_SECRET\' Environment Variables")
