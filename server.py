import os
import json

from aiohttp import web
from discord import Embed, Client
from datetime import datetime
from bson.json_util import dumps
from resources.db import Database
from resources.webhook import Webhook
from resources.color import random_color

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())

BOT = Client()
ROUTES = list()
DB = Database(None)
DBL_AUTH = _auth["_t__auth_webhook"]
WEBHOOK = Webhook(url=_auth["_t__webhook_topgg"])
LINK_VOTE = "https://top.gg/bot/478977311266570242/vote"


def html_response(html_patch):
    html_file = open(html_patch, "r")
    return web.Response(status=200, text=html_file.read(), content_type='text/html')


async def index(request):
    if request:
        return html_response('web/index.html')


async def get_guild(request):
    try:
        _ID = int(request.match_info['guild_id'])
    except ValueError:
        _ID = 0
    CL = await DB.cd("guilds")
    DATA = await CL.find_one({"guild_id": _ID})
    if DATA is not None:
        JSON_DATA = dumps(DATA)
        return web.Response(status=200, text=f"{JSON_DATA}")
    return web.Response(status=401, text="SERVIDOR/GUILD INEXISTENTE")


async def get_user(request):
    try:
        _ID = int(request.match_info['user_id'])
    except ValueError:
        _ID = 0
    CL = await DB.cd("users")
    DATA = await CL.find_one({"user_id": _ID})
    if DATA is not None:
        JSON_DATA = dumps(DATA)
        return web.Response(status=200, text=f"{JSON_DATA}")
    return web.Response(status=401, text="USUARIO/MEMBER INEXISTENTE")


async def top_gg(request):
    _AUTH_POST = request.headers.get("Authorization", "")
    DATA = await request.json()
    if _AUTH_POST == DBL_AUTH:
        USER = await BOT.fetch_user(int(DATA["user"]))
        ASH = await BOT.fetch_user(int(DATA["bot"]))
        AVATAR = USER.avatar_url if USER is not None else None
        THUMBNAIL = AVATAR if AVATAR is not None else ASH.avatar_url
        NAME = USER if USER is not None else "TEST"
        WEBHOOK.embed = Embed(
            colour=random_color(),
            description=f"O membro **{NAME}** `[{DATA['user']}]` votou no bot **[{ASH}]({LINK_VOTE})**",
            timestamp=datetime.utcnow()
        ).set_thumbnail(
            url=THUMBNAIL
        ).to_dict()
        await WEBHOOK.send()
        return web.Response(status=200, text="WEBHOOK ENVIADO COM SUCESSO!")
    return web.Response(status=401, text="Authorization failed")


async def make_app():
    global BOT
    await BOT.login(token=_auth['_t__ashley'])

    ROUTES.append(web.get('/', index))
    ROUTES.append(web.post('/top_gg', top_gg))
    ROUTES.append(web.get('/user/{user_id}', get_user))
    ROUTES.append(web.get('/guild/{guild_id}', get_guild))

    app = web.Application()
    app.add_routes(ROUTES)
    app.router.add_static('/css/', path='web/static', name='css')
    app.router.add_static('/image/', path='web/image', name='image')
    return app


web.run_app(make_app(), port=int(os.environ["PORT"]))
