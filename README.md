# Spotify Bot Message Injecter
Its creation was the idea that if you send commands from anywhere like a phone sms, it would
control spotify

# Install
## Prerequisites 
1. A Web Proxy
2. Redis
3. Docker

# Steps
1. Just run `docker run -d -p 5000:5000 -env CLIENT_ID="CLIENT_ID from spotify" --env CLIENT_SECRET="CLIENT_SECRET from spotify" --env APP_ENV="Production" shreyajj/spotifybot:latest`
2. Go to "https://your.site/login" to be prompted for login. If you need to login, it will redirect you. If you need to know what the login redirect url it needs go to the home page and it should show you on the logs portion of the page.
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
* `!!next` - Skips songs to current device playing
* `!!back` - Go back a song to current device playing
* `!!fplay "Song to play"` - Searches for the song and force play the song for the current device playing
* `!!volume "a number from 0-100"` - Changes the volume for the current device

# Im sure this works without docker but haven't really tested it that much

