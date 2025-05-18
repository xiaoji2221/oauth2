from flask import Flask, redirect, request, session
import requests
import os
import urllib.parse


app = Flask(__name__)
app.secret_key = os.urandom(24)


CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:5050/callback'

DISCORD_API_BASE_URL = "https://discord.com/api"
OAUTH2_AUTHORIZE_URL = DISCORD_API_BASE_URL + "/oauth2/authorize"
OAUTH2_TOKEN_URL = DISCORD_API_BASE_URL + "/oauth2/token"

SCOPE = "identify"

@app.route("/")
def home():
    return '<a href="/login">Login con Discord</a>'

@app.route("/login")
def login():
    redirect_uri_enc = urllib.parse.quote(REDIRECT_URI, safe='')
    return redirect(
        f"{OAUTH2_AUTHORIZE_URL}?client_id={CLIENT_ID}&redirect_uri={redirect_uri_enc}&response_type=code&scope={SCOPE}"
    )

@app.route("/callback")
def callback():
    code = request.args.get('code')
    if not code:
        return "Nessun codice ricevuto", 400

    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(OAUTH2_TOKEN_URL, data=data, headers=headers)
    if r.status_code != 200:
        return f"Errore nel token exchange: {r.text}", 500

    tokens = r.json()
    access_token = tokens['access_token']


    user_info = requests.get(
        DISCORD_API_BASE_URL + "/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    session['user'] = user_info
    return f"Ciao {user_info['username']}#{user_info['discriminator']}!<br><img src='https://cdn.discordapp.com/avatars/{user_info['id']}/{user_info['avatar']}.png' />"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=5050)
