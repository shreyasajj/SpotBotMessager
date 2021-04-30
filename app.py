import os
from datetime import datetime
from time import sleep

import spotipy
from flask import Flask, request, render_template, redirect
from spotipy.oauth2 import SpotifyOAuth

from api import api
import config
from config.logger import loggingWrite
from config.logger import logFileName
import config.Application as application


#

def getDifference(then, now=datetime.now(), interval="secs"):
    duration = now - then
    duration_in_s = duration.total_seconds()

    # Date and Time constants
    yr_ct = 365 * 24 * 60 * 60  # 31536000
    day_ct = 24 * 60 * 60  # 86400
    hour_ct = 60 * 60  # 3600
    minute_ct = 60

    def yrs():
        return divmod(duration_in_s, yr_ct)[0]

    def days():
        return divmod(duration_in_s, day_ct)[0]

    def hrs():
        return divmod(duration_in_s, hour_ct)[0]

    def mins():
        return divmod(duration_in_s, minute_ct)[0]

    def secs():
        return duration_in_s

    return {
        'yrs': int(yrs()),
        'days': int(days()),
        'hrs': int(hrs()),
        'mins': int(mins()),
        'secs': int(secs())
    }[interval]


def create_app():
    print(f'Starting app in {config.APP_ENV} environment')
    flask_app = Flask(__name__)
    flask_app.config.from_object('config')
    api.init_app(flask_app)

    @flask_app.route('/', methods=['GET'])
    def index():
        return render_template("index.html")

    @flask_app.before_first_request
    def start():
        num_token = 1
        try:
            num_token = int(os.environ["NUM_TOKENS"])
        except ValueError as e:
            num_token = 1
        except KeyError as e:
            num_token = 1
        if not os.path.isfile(application.tokenFileName) or len(open(application.tokenFileName).readlines()) != num_token:
            application.random_string_generator(50, num_token)
            loggingWrite("Created " + str(num_token) + " token(s)", "System")




    @flask_app.route('/login', methods=['GET'])
    def spotifyLogin():

        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path='data/.cache')
        auth_manager = SpotifyOAuth(client_id=os.environ["CLIENT_ID"],
                                    client_secret=os.environ["CLIENT_SECRET"],
                                    redirect_uri=request.host_url + "login",
                                    scope="user-modify-playback-state "
                                          "user-read-playback-state "
                                          "user-read-recently-played",
                                    cache_handler=cache_handler)
        if request.args.get("code"):
            # Step 3. Being redirected from Spotify auth page
            auth_manager.get_access_token(request.args.get("code"))
            loggingWrite("Logged In", "System")
            print("Need to login Redirecting")
            return redirect('/')
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            # Step 2. Display sign in link when no token
            auth_url = auth_manager.get_authorize_url()
            print("Need to login Redirecting")
            print("Redirect URL is: " + request.host_url + "login")
            loggingWrite("REDIRECT URL is: " + request.host_url + "login", "System")
            loggingWrite("Need to login Redirecting", "System")
            return redirect(auth_url)
        loggingWrite("Already Login Passing on", "System")
        return redirect('/')

    @flask_app.route('/stream', methods=['GET'])
    def stream():
        def generate():
            while not os.path.isfile(logFileName):
                sleep(1)
            with open(logFileName) as f:
                withinTime = True
                while True:
                    failed = False
                    debug = f.readline()
                    try:
                        datetimeValue = debug.split(" - ")
                        date = datetime.strptime(datetimeValue[0], "%b-%d-%Y %X")
                        if getDifference(date, datetime.now(), 'hrs') < 11:
                            withinTime = True
                            yield debug
                        else:
                            withinTime = False
                    except ValueError as e:
                        failed = True
                    if failed:
                        if withinTime:
                            yield debug
                    # yield date
                    while not os.path.isfile(logFileName):
                        sleep(1)
                    sleep(.05)

        return flask_app.response_class(generate(), mimetype='text/plain')

    return flask_app


if __name__ == '__main__':

    if "CLIENT_ID" in os.environ and "CLIENT_SECRET" in os.environ:
        app = create_app()
        app.run()
    else:
        print("Please Provide \'CLIENT_ID\' and \'CLIENT_SECRET\' Environment Variables")
