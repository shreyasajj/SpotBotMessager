# Spotify Bot Message Injecter
It creation was the idea that if you send commands from anywhere like a phone sms that would
control spotify

# Install
## Prerequisites 
1. Get a web Proxy
2. Get redis
3. Docker install

# Steps
1. Just run `docker run -d -p 5000:5000 -env CLIENT_ID="CLIENT_ID from spotify" --env CLIENT_SECRET="CLIENT_SECRET from spotify" --env APP_ENV="Production" shreyajj/spotifybot:latest`
2. Go to "https://your.site/login" to be prompted for login. If you need to login, it will redirect you. If you need to know what the login redirect url it needs go to the home page and it should show you on the logs portion of the page.
3. Hit the endpoint "https://your.site/api/message" with a `post` request having a body in `form-data` containing `name = "User asking permision"` and `message="asking/command"` (message must start with `!`)

### Im sure this works without docker but haven't really tested it that much

