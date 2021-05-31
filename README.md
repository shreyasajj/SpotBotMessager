# Spotify Bot Message Injecter
This creation was the idea that if you send commands from anywhere like a SMS, it would be able to 
control spotify if given the right parameters

# Install
## Prerequisites 
1. A Web Proxy
2. Redis
3. Docker

# Steps
1. Just run `docker run -d -p 5000:5000 -env CLIENT_ID="CLIENT_ID from spotify" --env CLIENT_SECRET="CLIENT_SECRET from spotify" --env APP_ENV="Production" shreyajj/spotifybot:latest`
2. Go to "https://your.site/login" to be prompted for login. If you need to login, it will redirect you. If you need to know what the login redirect url, go to the home page and it should show you the redirect Url on the page like `REDIRECT URL: http://your.site/login"`.
3. Hit the endpoint "https://your.site/api/message" with a `post` request having a body in `form-data` containing `name = "User asking permision"` and `message="asking/command"` (message must start with `!`)

# Environmental Variable
## https://developer.spotify.com/dashboard/login
* CLIENT_ID= "Get from spotify"
* CLIENT_SECRET = "Get from spotify"
* APP_ENV = "Choose: 'Production', 'Test', 'Development'"

## Optional
* NUM_TOKEN = "Created a number of application token to be check for any api request"

# Mount File
Can mount `/app/data` to any folder. Example `-v /data:/app/data`. 
After everything setup you will see 3 files in the mounted folder
* token.txt
* Logging.txt
* .cache

# Commands
* `!"Any song"` - Adds to Queue to current device playing
* `!!next` - Skips songs on the current device playing
* `!!back` - Go back a song on the current device playing
* `!!fplay "Song to play"` - Searches for the song and force play the song for the current device playing
* `!!volume "a number from 0-100"` - Changes the volume for the current device
* `!!queue` - Shows the current queue in a makeshift version. No made way to see the spotify queue

# Im sure this works without docker but haven't really tested it that much

