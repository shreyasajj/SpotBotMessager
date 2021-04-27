import os
import time
from datetime import datetime

from flask import jsonify, request
from flask_restful import Api, Resource
from tasks import celery
import config

import spotipy

api = Api(prefix=config.API_PREFIX)


def logging(log, contact):
    f = open("Logging.txt", "a+")
    f.write(str(datetime.now().strftime("%b-%d-%Y %X")) + " - " + contact + " - " + log + "\n")
    f.close()


class SpotifyConnect(Resource):
    def post(self):
        name = request.form.get("name", None)
        messageVal = request.form.get("message", None)
        if name and messageVal:
            provider = name
            cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path='.cache')
            auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=os.environ["CLIENT_ID"],
                                                       client_secret=os.environ["CLIENT_SECRET"],
                                                       redirect_uri=request.host_url + "login",
                                                       cache_handler=cache_handler)
            if not auth_manager.validate_token(cache_handler.get_cached_token()):
                logging("Need to login", "System")
                return {'message': "Please Login to :" + request.host_url + "login"}, 309

            sp = spotipy.Spotify(auth_manager=auth_manager)

            message = messageVal
            if message.startswith("!"):
                temp = message[1:].strip().lower()
                if temp != "!" and temp != "" and temp != "!!":
                    try:
                        if temp.startswith("!"):
                            text = temp[1:].strip().lower()
                            command = text.split(" ")[0]
                            notcommand = text.replace(command, "").strip()
                            if command == "next":
                                nexttrack(sp)
                                logging("Moved to next Song", provider)
                                return {'message': "Moved to next song"}, 200
                            elif command == "back":
                                backtrack(sp)
                                logging("Moved to previous Song", provider)
                                return {'message': "Moved to previous song"}, 200
                            elif command == "fplay":
                                search = notcommand.replace(" ", "+").lower()
                                results = searchSpot(sp, search)
                                for idx, track in enumerate(results['tracks']['items']):
                                    forcePlay(sp, track["uri"])
                                    found = False
                                    Artist = ""
                                    for index, artists in enumerate(track["album"]["artists"]):
                                        Artist += artists["name"] + ", "
                                        found = True
                                    if not found:
                                        Artist = "No found artist"
                                    else:
                                        Artist = Artist[0:-2]
                                    logging("Forced Played: " + track["name"] + " By:" + Artist + " -------------- Link: " +
                                            track["external_urls"]["spotify"], provider)
                                    return {'message': "Forced Played: " + track["name"] + "\nBy:" + Artist + "\nLink: " + \
                                                       track["external_urls"]["spotify"]}, 200
                            elif command == "vol" or command == "volume":
                                try:
                                    vol = int(notcommand)
                                    changeVolume(sp, vol)
                                    logging("Volume changed to " + str(vol), provider)
                                    return {'message': "Volume Changed to " + str(vol)}, 200
                                except ValueError as e:
                                    logging("Error: "+notcommand+" was not a Integer", provider)
                                    return {'message': "Error: Not a Integer"}, 200
                            else:
                                return {'message': "Command not found"}, 200
                        else:
                            searchString = temp.replace(" ", "+").lower()
                            results = searchSpot(sp, searchString)
                            sent = False
                            for idx, track in enumerate(results['tracks']['items']):
                                addQueue(sp, track["uri"])
                                found = False
                                Artist = ""
                                for index, artists in enumerate(track["album"]["artists"]):
                                    Artist += artists["name"] + ", "
                                    found = True
                                if not found:
                                    Artist = "No found artist"
                                else:
                                    Artist = Artist[0:-2]
                                logging("Added " + track["name"] + " By:" + Artist + " ---------- Link: " + \
                                        track["external_urls"]["spotify"], provider)
                                return {'message': "Added " + track["name"] + "\nBy:" + Artist + "\nLink: " + \
                                                   track["external_urls"]["spotify"]}, 200
                            if not sent:
                                logging("No results for " + temp, provider)
                                return {'message': "Did not add: There were no results"}, 200
                    except spotipy.SpotifyException as error:
                        if error.reason != "NO_ACTIVE_DEVICE":
                            raise Exception
                        else:
                            logging("Error: Spotify not active: " + str(error), provider)
                            return {'message': "Error: Spotify not active"}, 428
                    except Exception as e:
                        logging("Error: " + str(e), provider)
                        return {'message': "Error: " + str(e)}, 401
                else:
                    logging("Nothing was provided", provider)
                    return {'message': "Error: There was nothing provided"}, 404
            else:
                logging("Did not have a message that started with !", provider)
                return {'message': "Must start with !"}, 400
        else:
            logging("Did not provide phone number or message", "unknown")
            return {'message': "Must have \'name\' and \'message\'"}, 400
        logging("Error: Nothing was matched How is that possible", "Unknown")
        return {'message': "Error: Nothing was matched"}, 200


@celery.task()
def nexttrack(sp):
    sp.next_track()


@celery.task()
def backtrack(sp):
    sp.previous_track()


@celery.task()
def searchSpot(sp, search):
    return sp.search(q=search, type="track", limit=1)


@celery.task()
def forcePlay(sp, play):
    sp.start_playback(uris=[play])


@celery.task()
def addQueue(sp, play):
    sp.add_to_queue(uri=play)

@celery.task()
def changeVolume(sp, volume):
    sp.volume(volume)


# data processing endpoint
api.add_resource(SpotifyConnect, '/message')

