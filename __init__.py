# Dolyement Works HUH
from typing import MutableSequence
import nextcord
from nextcord.ext import commands
from quart import Quart, redirect, url_for, render_template, request
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from dotenv import load_dotenv
import os
from nextcord.ext import ipc

PREFIX = ["a-", "A-"]

bot = commands.Bot(command_prefix=PREFIX, intents=nextcord.Intents.all())

load_dotenv()
TOKEN = os.getenv("dsc_token")
RI = os.getenv("RI")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
session = os.getenv("quart_key")

app = Quart(__name__)
ipc_client = ipc.Client(secret_key="youshallnotpass")

# Initializing the Quart Website
app.secret_key = f'{session}'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = f'{CLIENT_ID}'
app.config["DISCORD_CLIENT_SECRET"] = f'{CLIENT_SECRET}'
app.config["DISCORD_REDIRECT_URI"] = f'{RI}'
app.config["DISCORD_BOT_TOKEN"] = f'{TOKEN}'

discordd = DiscordOAuth2Session(app)


@app.route("/home/")
async def index():
    return redirect(url_for(".home"))

# init html files


@app.route("/")
async def home():
    return await render_template("index.html", logged=await discordd.authorized)


@app.route("/help/")
@requires_authorization
async def help():
    return await render_template("help.html")


@app.route("/about/")
async def about():
    return await render_template("")


@app.route("/dashboard/")
@requires_authorization
async def dashboard():
    guild_count = await ipc_client.request("guild_count")
    guilds = await ipc_client.request("guilds_in")
    user_guilds = await discordd.fetch_guilds()
    guild_icon = await ipc_client.request("guilds_icon")
    mutual_guilds = []
    for guild in user_guilds:
        if guild.id in guilds:
            mutual_guilds.append(guild)

    return await render_template("dash.html", guild_count=guild_count, matching=mutual_guilds, guild_icon=guild_icon)


@app.route("/login/")
async def login():
    return await discordd.create_session()


@app.route("/logout/")
async def logout():
    logged = False
    discordd.revoke()

    return redirect(url_for(".home"))


@app.route("/me/")
@requires_authorization
async def me():
    user = await discordd.fetch_user()
    return redirect(url_for(".dashboard"))


@app.route("/callback/")
async def callback():
    logged = True
    try:
        await discordd.callback()
    except:
        return redirect(url_for(".login"))
    return redirect(url_for(".home"))


@app.errorhandler(Unauthorized)
async def redirect_unauthorized(e):
    bot.url = request.url
    return redirect(url_for(".login"))


if __name__ == '__main__':
    # app.run(host="0.0.0.0", port=PORT, debug=True)
    app.run(debug=True)
