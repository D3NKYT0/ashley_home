import os
import json
import jinja2
import logging
import aiohttp_jinja2

from resources.crypto import decrypt_text
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


def number_convert(number):
    a = '{:,.0f}'.format(float(number))
    b = a.replace(',', 'v')
    c = b.replace('.', ',')
    d = c.replace('v', '.')
    return d


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


@aiohttp_jinja2.template('user.html')
async def get_user(request):
    print(await request.text())
    try:
        _ID = int(request.match_info['user_id'])
    except ValueError:
        _ID = 0
    CL = await DB.cd("users")
    DATA = await CL.find_one({"user_id": _ID})
    if DATA is not None:
        USER = await BOT.fetch_user(_ID)
        ABOUT_DEFAULT = "Mude seu about, usando o comando \"ash about <text>\""
        NAME, DESC, AVATAR = USER.name, USER.discriminator, USER.avatar_url
        NAMES, LEVELS = list(), list()
        ABOUT = DATA["user"]["about"] if DATA["user"]["about"] != ABOUT_DEFAULT else "Nenhum About me"
        CLASS = DATA["rpg"]["class_now"] if DATA["rpg"]["class_now"] else "Nenhuma Classe"
        if DATA["rpg"]["class_now"]:
            for k in DATA["rpg"]["sub_class"]:
                if k.lower() != DATA["rpg"]["class_now"].lower():
                    NAMES.append(k)
                    LEVELS.append(DATA["rpg"]["sub_class"][k]["level"])

        DATA_GERAL = [
                      f'Commands: {DATA["user"]["commands"]}',
                      f'Rec: {DATA["user"]["rec"]}',
                      f'Wallet: {number_convert(DATA["treasure"]["money"])}',
                      f'Coin: {number_convert(DATA["inventory"]["coins"])}'
                     ]
        data = {
                'id': _ID,
                'name': NAME,
                'descri': DESC,
                'img': AVATAR,
                'class': CLASS,
                'about': ABOUT,
                'level': DATA["user"]["level"],
                'data_geral': DATA_GERAL,
                'classn': NAMES,
                'classl': LEVELS
                }
        return data
    return web.Response(status=401, text="USUARIO/MEMBER INEXISTENTE")


async def get_userapi(request):
    try:
        _ID = int(request.match_info['user_id'])
    except ValueError:
        _ID = 0
    CL = await DB.cd("users")
    DATA = await CL.find_one({"user_id": _ID})
    if DATA is not None:
        JSON_DATA = dumps(DATA, indent=4)
        return web.Response(status=200, text=f"{JSON_DATA}", content_type="application/json")
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


@aiohttp_jinja2.template('code.html')
async def adfly(request):
    if request:
        return {'code': 'Use o comando "ash adfly"'}


@aiohttp_jinja2.template('code.html')
async def adflycode(request):
    CL = await DB.cd("adfly")
    DATA = await CL.find_one({"code": request.match_info["code"]})
    KEY, IV = DATA["key"], DATA["iv"]
    code = decrypt_text(request.match_info["code"], IV, KEY)
    return {'code': code}


async def make_app():
    global BOT
    await BOT.login(token=_auth['_t__ashley'])

    ROUTES.append(web.get('/', index))
    ROUTES.append(web.post('/top_gg', top_gg))
    ROUTES.append(web.get('/user/{user_id}', get_user))
    ROUTES.append(web.get('/user/{user_id}/api', get_userapi))
    ROUTES.append(web.get('/guild/{guild_id}', get_guild))
    ROUTES.append(web.get('/adfly', adfly))
    ROUTES.append(web.get('/adfly/{code}', adflycode))

    app = web.Application()
    app.add_routes(ROUTES)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('web'))
    env = aiohttp_jinja2.get_env(app)
    env.globals.update(zip=zip)
    app.router.add_static('/css/', path='web/static', name='css')
    app.router.add_static('/image/', path='web/image', name='image')
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    web_logger = logging.getLogger("aiohttp.web")
    web.run_app(make_app(), port=int(os.environ["PORT"]), access_log=web_logger)
