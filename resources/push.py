import json
from onesignal import OneSignal as OneClient, SegmentNotification

with open("data/auth.json") as auth:
    _auth = json.loads(auth.read())


class OneSignal(object):
    def __init__(self):
        self._push = OneClient(_auth["_t__push_id"], _auth["_t__push_key"])

    def send(self, content, url="https://github.com/D3NKYT0/ashley_home/wiki"):
        """
        O conteudo do parametro "content" deve ser sempre um dict()
        :param content:
        :param url:
        :return:
        """

        if type(content) is dict():
            raise "O conteudo de 'content' deve ser sempre um DICT()"

        notification_to_all_users = SegmentNotification(
            contents={"en": content["en"], "pt": content["pt"]},
            included_segments=SegmentNotification.ALL, url=url)
        self._push.send(notification_to_all_users)
