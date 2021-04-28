import os
from datetime import datetime
from flask import request
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
        try:
            if name and messageVal:
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
                                    logging("Moved to next Song", name)
                                    return {'message': "Moved to next song"}, 200
                                elif command == "back":
                                    backtrack(sp)
                                    logging("Moved to previous Song", name)
                                    return {'message': "Moved to previous song"}, 200
                                elif command == "fplay":
                                    playReturn = searchAndPlaySpot(notcommand, sp, forcePlay)
                                    if playReturn:
                                        track = playReturn[0]
                                        Artist = playReturn[1]
                                        logging("Forced Played: " + track[
                                            "name"] + " By:" + Artist + " -------------- Link: " +
                                                track["external_urls"]["spotify"], name)
                                        return {'message': "Forced Played: " + track[
                                            "name"] + "\nBy:" + Artist + "\nLink: " + \
                                                           track["external_urls"]["spotify"]}, 200
                                    else:
                                        logging("Force Play: No results for " + temp, name)
                                        return {'message': "Did not play: There were no results"}, 200
                                elif command == "vol" or command == "volume":
                                    try:
                                        vol = int(notcommand)
                                        changeVolume(sp, vol)
                                        logging("Volume changed to " + str(vol), name)
                                        return {'message': "Volume Changed to " + str(vol)}, 200
                                    except ValueError as e:
                                        logging("Error: " + notcommand + " was not a Integer", name)
                                        return {'message': "Error: Not a Integer"}, 200
                                else:
                                    return {'message': "Command not found"}, 200

                            else:
                                playReturn = searchAndPlaySpot(temp, sp, addQueue)
                                if playReturn:
                                    track = playReturn[0]
                                    Artist = playReturn[1]
                                    logging("Added " + track["name"] + " By:" + Artist + " ---------- Link: " + \
                                            track["external_urls"]["spotify"], name)
                                    return {'message': "Added " + track["name"] + "\nBy:" + Artist + "\nLink: " + \
                                                       track["external_urls"]["spotify"]}, 200
                                else:
                                    logging("Queue: No results for " + temp, name)
                                    return {'message': "Did not add: There were no results"}, 200
                        except spotipy.SpotifyException as error:
                            if error.reason == "NO_ACTIVE_DEVICE":
                                logging("Error: Spotify not active: " + str(error), name)
                                return {'message': "Error: Spotify not active"}, 428
                            elif error.reason == "VOLUME_CONTROL_DISALLOW":
                                logging("Error: Volume Cannot Be Controlled: " + str(error), name)
                                return {'message': "Volume Cannot Be Controlled"}, 200
                            else:
                                raise error

                    else:
                        logging("Nothing was provided", name)
                        return {'message': "Error: There was nothing provided"}, 404
                else:
                    logging("Did not have a message that started with !", name)
                    return {'message': "Must start with !"}, 422
            else:
                logging("Did not provide phone number or message", "unknown")
                return {'message': "Must have \'name\' and \'message\'"}, 422
        except Exception as e:
            logging("Error: " + str(e) + " --- Command is: " + str(messageVal), name)
            return {'message': "Error Occurred "}, 400
        logging("Error: Nothing was matched How is that possible. The command is : " + str(messageVal), "Unknown")
        return {'message': "Error: Nothing was matched"}, 400


def searchAndPlaySpot(inputVal, sp, command):
    searchString = inputVal.replace(" ", "+").lower()
    results = searchSpot(sp, searchString)
    sent = False
    for idx, track in enumerate(results['tracks']['items']):
        command(sp, track["uri"])
        found = False
        Artist = ""
        for index, artists in enumerate(track["album"]["artists"]):
            Artist += artists["name"] + ", "
            found = True
        if not found:
            Artist = "No found artist"
        else:
            Artist = Artist[0:-2]
        return [track, Artist]

    if not sent:
        return False


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
