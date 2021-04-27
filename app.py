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
    app = Flask(__name__)
    app.config.from_object('config')
    api.init_app(app)

    # @app.before_first_request
    # def beforeAnything():
    #     fname = "Logging.txt"
    #     if os.path.isfile(fname):
    #         os.remove(fname)

    @app.route('/', methods=['GET'])
    def index():
        print(request.host_url)
        hi = request
        print(str(request.is_secure))
        return render_template("index.html")

    @app.route('/login', methods=['GET'])
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

    @app.route('/stream', methods=['GET'])
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

        return app.response_class(generate(), mimetype='text/plain')

    return app


# @app.route('/message', methods=['POST'])
# def message():
#     name = request.form.get("name", None)
#     messageVal = request.form.get("message", None)
#     if name and messageVal:
#         provider = name
#         cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path='.cache')
#         auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=os.environ["CLIENT_ID"],
#                                                    client_secret=os.environ["CLIENT_SECRET"],
#                                                    redirect_uri=request.host_url+"login",
#                                                    cache_handler=cache_handler)
#         if not auth_manager.validate_token(cache_handler.get_cached_token()):
#             logging("Need to login", "System")
#             return {'message': "Please Login to :"+request.host_url+"login"}, 401
#
#         sp = spotipy.Spotify(auth_manager=auth_manager)
#
#         temp = messageVal
#         if temp.startswith("!"):
#             temp2 = temp[1:].strip().replace(" ", "+").lower()
#             try:
#                 if temp2 == "!next":
#                     sp.next_track()
#                     logging("Moved to next Song", provider)
#                     return {'message': "Moved to next song"}, 200
#                 elif temp2 == "!back":
#                     sp.previous_track()
#                     logging("Moved to previous Song", provider)
#                     return {'message': "Moved to previous song"}, 200
#                 elif temp2.startswith("!fplay"):
#                     search = temp2[6:].strip("+").replace(" ", "+").lower()
#                     results = sp.search(q=search, type="track", limit=1)
#                     for idx, track in enumerate(results['tracks']['items']):
#                         # print(track["uri"])
#                         sp.start_playback(uris=[track["uri"]])
#                         found = False
#                         Artist = ""
#                         for index, artists in enumerate(track["album"]["artists"]):
#                             Artist += artists["name"] + ", "
#                             found = True
#                         if not found:
#                             Artist = "No found artist"
#                         else:
#                             Artist = Artist[0:-2]
#                         logging("Forced Played: " + track["name"] + " By:" + Artist + " -------------- Link: " +
#                                 track["external_urls"]["spotify"], provider)
#                         return {'message': "Forced Played: " + track["name"] + "\nBy:" + Artist + "\nLink: " + \
#                                            track["external_urls"]["spotify"]}, 200
#                 else:
#                     results = sp.search(q=temp2, type="track", limit=1)
#                     sent = False
#                     for idx, track in enumerate(results['tracks']['items']):
#                         sent = True
#                         sp.add_to_queue(uri=track["uri"])
#                         found = False
#                         Artist = ""
#                         for index, artists in enumerate(track["album"]["artists"]):
#                             Artist += artists["name"] + ", "
#                             found = True
#                         if not found:
#                             Artist = "No found artist"
#                         else:
#                             Artist = Artist[0:-2]
#                         logging("Added " + track["name"] + " By:" + Artist + " ---------- Link: " + \
#                                 track["external_urls"]["spotify"], provider)
#                         return {'message': "Added " + track["name"] + "\nBy:" + Artist + "\nLink: " + \
#                                            track["external_urls"]["spotify"]}, 200
#                     if not sent:
#                         logging("No results for " + temp2, provider)
#                         return {'message': "Did not add: There were no results"}, 404
#             except Exception as e:
#                 logging("Spotify not active" + str(e), provider)
#                 return {'message': "Error: Spotify not active"}, 401
#         else:
#             logging("Did not have a message that started with !", provider)
#             return {'message': "Must start with !"}, 400
#     else:
#         logging("Did not provide phone number or message", "unknown")
#         return {'message': "Must have \'name\' and \'message\'"}, 400

if __name__ == '__main__':

    if "CLIENT_ID" in os.environ and "CLIENT_SECRET" in os.environ:
        app = create_app()
        app.run()
    else:
        print("Please Provide \'CLIENT_ID\' and \'CLIENT_SECRET\' Environment Variables")
