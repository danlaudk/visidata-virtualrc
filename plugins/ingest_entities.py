from visidata import *
import requests
import math
from time import sleep

vd.option('virtualrc_app_id', '', 'app id for virtual RC')
vd.option('virtualrc_app_secret', '', 'secret key for virtual RC')


@Sheet.api
def get_dict_of_rows(sheet):
    def array_dict_to_dict_two_list(array_dict):
        key1 = list(array_dict[0].keys())[0]
        key2 = list(array_dict[0].keys())[1]
        manylists = [list(i.values()) for i in array_dict]
        twolists = [[li[i] for li in manylists] for i in range(2)]
        return {key1: twolists[0], key2: [math.trunc(i) for i in twolists[1]]}

    array_dicts = [{col.name: val for col, val in dispvals.items()} for dispvals in sheet.iterdispvals()]
    print(array_dicts)
    dict_of_two_list = array_dict_to_dict_two_list(array_dicts)
    PLOT_BOT = PlotBot()
    # dic = {'asd': ['one', "sdf sdf sdf ", ""], 'randint': [5, 3, 5]}

    PLOT_BOT.plot_named_horizontals(dict_of_two_list, 129, 109, "")


@Sheet.api
def plot_col_vertically(sheet):
    singlecol = [n for dispvals in sheet.iterdispvals() for n in list(dispvals.values())]
    # print("single col " + str(singlecol))
    PLOT_BOT = PlotBot()
    PLOT_BOT.plot(singlecol)

# requires use world sheet. clears all wall rows on sheet
# requires sort rows in reverse order of bot-build: on sheet nav to y, [, nav to x, z] (ie. sort asc y, 2ndry-sort desc x)
@Sheet.api
def clear_walls(sheet):
    array_dicts = [{col.name: val for col, val in dispvals.items()} for dispvals in sheet.iterdispvals()]
    PLOT_BOT = PlotBot()
    for d in array_dicts:
        PLOT_BOT._erase_wall(d['x'], d['y'], d['id'])

@Sheet.api
def daniel_cmd(sheet, d):
    vd.status(str(d))
    # send dictionary d to plot-bot


Sheet.addCommand('', 'virtualrc-plot-horizontal-second-col', 'daniel_cmd(get_dict_of_rows())')
Sheet.addCommand('', 'vertical-only-col-virtualrc', 'daniel_cmd(plot_col_vertically())')
Sheet.addCommand('', 'walls-remove-virtualrc', 'daniel_cmd(get_walls())')


@VisiData.api
def open_vrc(vd, p):
    return VirtualRCSheet(p.name, source=p)


class VirtualRCSheet(TableSheet):
    rowtype = 'entities'  # rowdef: dict from JSON response)
    # columns = [
    #     ItemColumn('msg_type', 'type'),
    #     ItemColumn('user', 'payload.person_name'),
    #     ItemColumn('id', 'payload.id', width=0),
    #     ItemColumn('type', 'payload.type'),
    #     ItemColumn('x', 'payload.pos.x', type=int),
    #     ItemColumn('y', 'payload.pos.y', type=int),
    #     ItemColumn('dir', 'payload.direction'),
    #     ItemColumn('muted', 'payload.muted'),
    #     ItemColumn('updated_at', 'payload.updated_at', type=date, fmtstr='%H:%M'),
    #     ItemColumn('payload.image_path', width=0),
    #     ItemColumn('user_id', 'payload.user_id', width=0),
    #     ItemColumn('last_present', 'payload.last_present_at', width=0, fmtstr='%H:%M'),
    #     ItemColumn('last_idle', 'payload.last_idle_at', width=0, fmtstr='%H:%M'),
    #     ItemColumn('payload.zoom_user_display_name', width=0),
    #     ItemColumn('payload.zoom_meeting_topic', width=0),
    #     ItemColumn('msg', 'payload.message.text'),
    #     ItemColumn('msg_sent', 'payload.message.sent_at', type=date),
    #     ItemColumn('payload.message.mentioned_entity_ids', type=vlen, width=0),
    # ]
    columns = [
        ItemColumn('msg_type', 'type'),
        ItemColumn('id', 'id', width=9),
        ItemColumn('x', 'pos.x', type=int),
        ItemColumn('y', 'pos.y', type=int),
        ItemColumn('user', 'person_name'),
        ItemColumn('dir', 'direction'),
        ItemColumn('muted', 'payload.muted'),
        ItemColumn('updated_at', 'updated_at', type=date, fmtstr='%H:%M'),
        ItemColumn('payload.image_path', width=0),
        ItemColumn('user_id', 'user_id', width=0),
        ItemColumn('last_present', 'last_present_at', width=0, fmtstr='%H:%M'),
        ItemColumn('last_idle', 'last_idle_at', width=0, fmtstr='%H:%M'),
        ItemColumn('payload.zoom_user_display_name', width=0),
        ItemColumn('payload.zoom_meeting_topic', width=0),
        ItemColumn('msg', 'message.text'),
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
    bot_message = {'text': 'A bot for collecting RC Together data'}

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
            # self.addRow(r.json())
            # get bot id
            r = requests.get(url=f"https://recurse.rctogether.com/api/bots?{self.creds}")
            # self.addRow(r.json())
            b_id = r.json()[0]['id']
            # update bot message
            r = requests.patch(url=f"https://recurse.rctogether.com/api/messages?bot_id={b_id}&{self.creds}",
                            json=self.bot_message)
            vd.status(f"update_bot status: {r.status_code}")
            for entity in msg["payload"]["entities"]:
                self.addRow(entity)


            # delete bot
#            r = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{b_id}?app_id={ID}&app_secret={SEC}")
        elif msg['type'] == 'entity':
            self.addRow(msg)
        else:
            vd.warning('unknown msg type "%s"' % msg['type'])
            self.addRow(msg)


# ==== REST API ================================================================

BOTURL = "https://recurse.rctogether.com/api/bots/"
NOTEURL = "https://recurse.rctogether.com/api/notes/"
WALLURL = "https://recurse.rctogether.com/api/walls/"
import os

ID = os.getenv('VIRTUALRCID')
SEC = os.getenv('VIRTUALRCSEC')


def post(id, j, url=BOTURL):
    return requests.post(url + str(id), json=j, auth=(ID, SEC))


def patch(id, j, url=BOTURL):
    return requests.patch(url + str(id), json=j, auth=(ID, SEC))


def delete(id, j=None, url=BOTURL):
    if j is None:
        return requests.delete(url + str(id), auth=(ID, SEC))
    else:
        return requests.delete(url + str(id), json=j, auth=(ID, SEC))


# ==== REST API ================================================================

class PlotBot:

    def __init__(self):
        self.b_id = 79126
        self.plotted = []
        print(f"[Plotter Bot {self.b_id}]: init")

    def post_wall(self, wall):
        self._move_to(wall['wall']['pos']['x'] + 1, wall['wall']['pos']['y'])
        self._orient('left')
        res = requests.post(
            url=f"https://recurse.rctogether.com/api/walls?app_id={ID}&app_secret={SEC}&bot_id={self.b_id}",
            json=wall)
        print("[Plotter Bot {self.b_id}]:" + str(res.status_code) + "end status." + str(res.json()) + " while trying to wall " + str(
            wall['wall']['pos']['x']) + ", " + str(wall['wall']['pos']['y']) + ", " + str(wall['wall']['wall_text']))
        if res.status_code is not None & (res.status_code == 200 | int(res.status_code) == 200):
            self.plotted.append((wall['wall']['pos']['x'], wall['wall']['pos']['y'], res.json()["id"]))
        else:
            print("RESPONSECODE SAD")
        return res

    def _erase_wall(self, x, y, idx):
        j = {"bot_id": self.b_id}
        res = self._move_to(x + 1, y)
        if res:
            res = delete(idx, j, WALLURL)
            if res.status_code != 200:
                print(f"[Plotter Bot {self.b_id}]:" + str(res.json()) + f"while deleting  x={x}, y={y}")
            else:
                print(f"[Plotter Bot {self.b_id}]: deleted wall x={x}, y={y}")
                return res

    def _move_to(self, x, y):
        jsn = {"bot": {"x": x, "y": y}}
        res = patch(self.b_id, jsn)
        if res.status_code != 200:
            print(f"[Plotter Bot {self.b_id}]:" + str(res.json()) + f"while moving to position x={x}, y={y}")
        else:
            print(f"[Plotter Bot {self.b_id}]: moved to x={x}, y={y}")
            return res

    def _orient(self, direct):
        jsn = {"bot": {"direction": direct}}
        patch(self.b_id, jsn)
        print(f"[Plotter Bot {self.b_id}]: changed orientation to {direct}")

    def clear(self):
        while self.plotted:
            x, y, idx = self.plotted.pop()
            self._erase_wall(x, y, idx)

        print(f"[Plotter Bot {self.b_id}]: walls cleared")

    # def clear(self):
    #     print("self" + str(self.b_id) +", self.plotted" + str(self.plotted))
    #     while self.plotted:
    #         x, y, idx = self.plotted.pop()
    #         print("start erase " + idx + " x:" + x)
    #         self._erase_wall(x, y, idx)
    #     print(f"[Plotter Bot {self.b_id}]: walls cleared")

    def file_out(self):
        import csv
        with open('./wallids.csv', 'w', newline='') as myfile:
            print(self.plotted)
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(self.plotted)

    @asyncthread
    def plot(self, list_str):
        list_int = list(map(lambda y: math.trunc(float(y)), filter(lambda x: (x != '') & (x is not None), list_str)))
        for idx, intg in enumerate(list_int):
            self.plot_int_vertical(intg, 100 + idx, 108)
            # self.plot_int_vertical_base10(i, 100 + i, 108, self.b_id)
        print(self.plotted)
        self.file_out()
        sleep(10)
        self.clear()

    def plot_int_vertical(self,  i, x, y):
        if i is not None:
            colours = ["gray", "pink", "orange", "green", "blue", "purple", "yellow"]
            willreversechars = [char for char in str(i)]
            willreversechars.reverse()
            for idx, char in enumerate(willreversechars):
                col = colours[idx % len(colours)]
                wall = {'wall': {'pos': {'x': x, 'y': y - idx}, 'color': col, 'wall_text': char}}
                res = self.post_wall(wall)
                print(f"update_wall status: {res.status_code}")

    # not ready
    def plot_int_vertical_base10(self, i, x, y0, base=10):
        colours = ["gray", "pink", "orange", "green", "blue", "purple", "yellow"]

        def plot_digit(i, divis, x, y):
            (q, r) = divmod(i, divis)
            col = colours[math.trunc(math.log10(divis))]
            wall = {'wall': {'pos': {'x': x, 'y': y}, 'color': col, 'wall_text': str(r)}}
            res = self.post_wall(wall)
            print(f"update_wall status: {res.status_code}")
            if q > 0:
                plot_digit(i, divis * base, x, y + 1)  # recursive call
            return 0  # no reason yet

        # plot walls out of integer i
        plot_digit(i, base, x, y0)

    def scale_vector(self, li_wall_lengths):
        if li_wall_lengths:
            if isinstance(li_wall_lengths[0], int) | isinstance(li_wall_lengths[0], float):
                if max(li_wall_lengths) > 20:
                    scale = max(li_wall_lengths) / 20
                    return [math.trunc(e / scale) for e in li_wall_lengths]
                else:
                    return li_wall_lengths
            else:
                print("error wall lengths not numeric")
        else:
            print("error: no wall lengths")

    # 129. 109 is bottomrow position
    # takes dict of two arrays, so call the above before passing to here.
    @asyncthread
    def plot_named_horizontals(self, dic, x, y, note_text):
        self.clear()
        names_to_write_on_walls = list(dic.values())[0]
        wall_lengths = self.scale_vector(list(dic.values())[1])
        colours = ["gray", "pink", "orange", "green", "blue", "purple", "yellow"]

        def plot_one_wall(graffiti, wall_length, x0, y0, col):
            for j in range(wall_length):
                graffiti_len = len(str(graffiti))
                wall_text = ' '  # default
                if j < graffiti_len:
                    wall_text = str(graffiti)[j]
                wall = {'wall': {'pos': {'x': x0 + j, 'y': y0}, 'color': col, 'wall_text': wall_text}}
                res = self.post_wall(wall)

        for k in range(len(names_to_write_on_walls)):
            col = colours[k % len(colours)]
            print("k " + str(k))
            print(str(names_to_write_on_walls))
            print(str(wall_lengths))
            plot_one_wall(names_to_write_on_walls[k], wall_lengths[k], x, y - k, col)

        print(self.plotted)
        self.file_out()
        # sleep(10)
        self.clear()
        # note_text = "Plot of " + str(list(dic.keys())[1]) + " against " + str(list(dic.keys())[0])
        # note = {'note': {'pos': {'x': x - 1, 'y': y}, 'note_text': note_text}}
        # res_note = requests.post(
        #     url=f"https://recurse.rctogether.com/api/notes?app_id={ID}&app_secret={SEC}&bot_id={self.b_id}",
        #     json=note)
        # print(res_note)
# end PlotBot
