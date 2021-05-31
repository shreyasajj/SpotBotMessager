import os
from datetime import datetime
from flask import request
from flask_restful import Api, Resource
from tasks import celery
import config

import spotipy
from config.logger import loggingWrite
from config.Application import validateToken
import time

api = Api(prefix=config.API_PREFIX)
lasttime=0
queue=[]
songdetails={}





class SpotifyConnect(Resource):
    def post(self):
        token = request.headers.get("API_Key", None)
        if not token:
            loggingWrite("No token provided", "System")
            return {'message': "No API Token Provided"}, 401
        if validateTokenValue(token):
            name = request.form.get("name", None)
            messageVal = request.form.get("message", None)
            try:
                if name and messageVal:
                    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path='data/.cache')
                    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=os.environ["CLIENT_ID"],
                                                               client_secret=os.environ["CLIENT_SECRET"],
                                                               redirect_uri=request.host_url + "login",
                                                               cache_handler=cache_handler)
                    if not auth_manager.validate_token(cache_handler.get_cached_token()):
                        loggingWrite("Need to login", "System")
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
                                        loggingWrite("Moved to next Song", name)
                                        return {'message': "Moved to next song"}, 200
                                    elif command == "back":
                                        backtrack(sp)
                                        loggingWrite("Moved to previous Song", name)
                                        return {'message': "Moved to previous song"}, 200
                                    elif command == "fplay":
                                        playReturn = searchAndPlaySpot(notcommand, sp, forcePlay)
                                        if playReturn:
                                            track = playReturn[0]
                                            Artist = playReturn[1]
                                            loggingWrite("Forced Played: " + track[
                                                "name"] + " By:" + Artist + " -------------- Link: " +
                                                    track["external_urls"]["spotify"], name)
                                            return {'message': "Forced Played: " + track[
                                                "name"] + "\nBy:" + Artist + "\nLink: " + \
                                                               track["external_urls"]["spotify"]}, 200
                                        else:
                                            loggingWrite("Force Play: No results for " + temp, name)
                                            return {'message': "Did not play: There were no results"}, 200
                                    elif command == "vol" or command == "volume":
                                        try:
                                            vol = int(notcommand)
                                            if vol>=0 and vol<=100:
                                                changeVolume(sp, vol)
                                                loggingWrite("Volume changed to " + str(vol), name)
                                                return {'message': "Volume Changed to " + str(vol)}, 200
                                            else:
                                                raise ValueError
                                        except ValueError as e:
                                            loggingWrite("Error: " + notcommand + " was not a valid number, must be between 0 and 100", name)
                                            return {'message': "Error: Not a Valid Number, must be between 0 and 100"}, 200
                                    elif command == "queue":
                                        if len(queue) != 0:
                                            previoussongs = previoussong(sp, int(songdetails[queue[0]][3]))
                                            for item in previoussongs["items"]:
                                                if item["track"]["id"] in queue:
                                                    queue.remove(item["track"]["id"])
                                                    if item["track"]["id"] in songdetails:
                                                        songdetails.pop(item["track"]["id"])
                                        currentsong = currentlyplaying(sp)
                                        if currentsong != None:
                                            if currentsong["item"]["id"] in queue:
                                                queue.remove(currentsong["item"]["id"])
                                                if currentsong["item"]["id"] in songdetails:
                                                    songdetails.pop(currentsong["item"]["id"])
                                            currentArtist=""
                                            found=False
                                            for index, artists in enumerate(currentsong["item"]["artists"]):
                                                currentArtist += artists["name"] + ", "
                                                found = True
                                            if not found:
                                                currentArtist = "No found artist"
                                            else:
                                                currentArtist = currentArtist[0:-2]
                                            returnmessage="Current Song: "+currentsong["item"]["name"]+ " By: "+currentArtist
                                            returnmessage+="\n----------------------------\nQueue:"
                                            number=1
                                            if len(queue) == 0:
                                                returnmessage+="\nNothing in Queue"
                                            for item in queue:
                                                songdet= songdetails[item]
                                                returnmessage+="\n"+str(number)+". "+songdet[1]+" By: "+songdet[2]+" -- Queued By:"+songdet[0]
                                                number+=1
                                            loggingWrite("Return Queue", name)
                                            return {'message': returnmessage}, 200

                                        else:
                                            raise spotipy.SpotifyException(http_status=404,
                                                                           code=-1,
                                                                           msg="!!queue\nPlayer command failed: No active device found",
                                                                           reason="NO_ACTIVE_DEVICE")


                                    else:
                                        return {'message': "Command not found"}, 200

                                else:
                                    playReturn = searchAndPlaySpot(temp, sp, addQueue)
                                    if playReturn:
                                        track = playReturn[0]
                                        Artist = playReturn[1]
                                        if len(queue) != 0:
                                            if time.time() - songdetails[queue[len(queue)-1]][3] > 21600:
                                                queue.clear()
                                                songdetails.clear()
                                        queue.append(track["id"])
                                        songdetails[track["id"]] = [name, track["name"], Artist, time.time()]
                                        loggingWrite("Added " + track["name"] + " By:" + Artist + " ---------- Link: " + \
                                                track["external_urls"]["spotify"], name)
                                        return {'message': "Added " + track["name"] + "\nBy:" + Artist + "\nLink: " + \
                                                           track["external_urls"]["spotify"]}, 200
                                    else:
                                        loggingWrite("Queue: No results for " + temp, name)
                                        return {'message': "Did not add: There were no results"}, 200
                            except spotipy.SpotifyException as error:
                                if error.reason == "NO_ACTIVE_DEVICE":
                                    queue.clear()
                                    songdetails.clear()
                                    loggingWrite("Error: Spotify not active: " + str(error), name)
                                    return {'message': "Error: Spotify not active"}, 428
                                elif error.reason == "VOLUME_CONTROL_DISALLOW":
                                    loggingWrite("Error: Volume Cannot Be Controlled: " + str(error), name)
                                    return {'message': "Volume Cannot Be Controlled"}, 200
                                else:
                                    raise error
                        else:
                            loggingWrite("Nothing was provided", name)
                            return {'message': "Error: There was nothing provided"}, 404
                    else:
                        loggingWrite("Did not have a message that started with !", name)
                        return {'message': "Must start with !"}, 422
                else:
                    loggingWrite("Did not provide phone number or message", "unknown")
                    return {'message': "Must have \'name\' and \'message\'"}, 422
            except Exception as e:
                loggingWrite("Error: " + str(e) + " --- Command is: " + str(messageVal), name)
                return {'message': "Error Occurred "}, 400
            loggingWrite("Error: Nothing was matched How is that possible. The command is : " + str(messageVal), "Unknown")
            return {'message': "Error: Nothing was matched"}, 400
        else:
            loggingWrite("Error: Token Invalid", "System")
            return {"message": "Error: Token must be valid"}, 401


@celery.task()
def validateTokenValue(Token):
    return validateToken(Token)


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
def currentlyplaying(sp):
    return sp.current_user_playing_track()

@celery.task()
def previoussong(sp, time):
    if time == 0:
        return sp.current_user_recently_played(limit=50)
    else:
        return sp.current_user_recently_played(after=time, limit=50)

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
