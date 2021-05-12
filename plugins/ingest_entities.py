from visidata import *

vd.option('virtualrc_app_id', '', 'app id for virtual RC')
vd.option('virtualrc_app_secret', '', 'secret key for virtual RC')


@Sheet.api
def get_dict_of_rows(sheet):
    return [{col.name:val for col,val in dispvals.items() } for dispvals in sheet.iterdispvals()]

@Sheet.api
def daniel_cmd(sheet, d):
    vd.status(str(d))

Sheet.addCommand('', 'daniel-cmd', 'daniel_cmd(get_dict_of_rows())')


@VisiData.api
def open_vrc(vd, p):
    return VirtualRCSheet(p.name, source=p)


class VirtualRCSheet(TableSheet):
    rowtype='entities'  # rowdef: dict from JSON response)
    columns=[
        ItemColumn('msg_type', 'type'),
        ItemColumn('user', 'payload.person_name'),
        ItemColumn('id', 'payload.id', width=0),
        ItemColumn('type', 'payload.type'),
        ItemColumn('x', 'payload.pos.x', type=int),
        ItemColumn('y', 'payload.pos.y', type=int),
        ItemColumn('dir', 'payload.direction'),
        ItemColumn('muted', 'payload.muted'),
        ItemColumn('updated_at', 'payload.updated_at', type=date, fmtstr='%H:%M'),
        ItemColumn('payload.image_path', width=0),
        ItemColumn('user_id', 'payload.user_id', width=0),
        ItemColumn('last_present', 'payload.last_present_at', width=0, fmtstr='%H:%M'),
        ItemColumn('last_idle', 'payload.last_idle_at', width=0, fmtstr='%H:%M'),
        ItemColumn('payload.zoom_user_display_name', width=0),
        ItemColumn('payload.zoom_meeting_topic', width=0),
        ItemColumn('msg', 'payload.message.text'),
        ItemColumn('msg_sent', 'payload.message.sent_at', type=date),
        ItemColumn('payload.message.mentioned_entity_ids', type=vlen, width=0),
    ]

    bot_info = {
        "bot": {
            "name": "VircDataBot",
            "emoji": "☃",
            "x": 54,
            "y": 44,
            "direction": "right",
            "can_be_mentioned": True,
        }
    }
    bot_message = { 'text': 'A bot for collecting RC Together data' }

    @property
    def creds(self):
        return f'app_id={self.options.virtualrc_app_id}&app_secret={self.options.virtualrc_app_secret}'

    @asyncthread
    def reload(self):
        from actioncable.connection import Connection
        from actioncable.subscription import Subscription
        con = Connection(origin='https://recurse.rctogether.com',
                         url=f'wss://recurse.rctogether.com/cable?{self.creds}')
        con.connect()

        self.sub = Subscription(con, identifier={"channel": "ApiChannel"})
        bot_message = {
            "text": "Hello, I am a bot run from example.py"
        }
        self.sub.on_receive(callback=self.sub_on_receive)

        self.sub.create()
        # sub.state

    def sub_on_receive(self, msg):
        if msg['type'] == "world":
            self.world = msg
            # initialize bot info
            r = requests.post(url=f"https://recurse.rctogether.com/api/bots?{self.creds}", json=self.bot_info)
            self.addRow(r.json())
            # get bot id
            r = requests.get(url=f"https://recurse.rctogether.com/api/bots?{self.creds}")
            self.addRow(r.json())
            b_id = r.json()[0]['id']
            # update bot message
            r = requests.patch(url=f"https://recurse.rctogether.com/api/messages?bot_id={b_id}&{self.creds}",
                            json=self.bot_message)
            vd.status(f"update_bot status: {r.status_code}")

            # delete bot
#            r = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{b_id}?app_id={ID}&app_secret={SEC}")
        elif msg['type'] == 'entity':
            self.addRow(msg)
        else:
            vd.warning('unknown msg type "%s"' % msg['type'])
            self.addRow(msg)
