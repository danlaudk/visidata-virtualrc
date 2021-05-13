import math

from actioncable.connection import Connection
from actioncable.subscription import Subscription
import requests
import time


def get_bot(bot_name: str, field: str = None, app_id: str = None, app_sec: str = None):
    if not app_id:
        app_id = ID
    if not app_sec:
        app_sec = SEC
    try:
        g = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={app_id}&app_secret={app_sec}")
        if field:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0][field]
        else:
            bot = list(filter(lambda x: x['name'] == bot_name, g.json()))[0]
    except IndexError:
        bot = False
    return bot


def get_bot():
    r = requests.get(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}")
    print(f"get_bot status: {r.status_code}")
    print(r.json())
    # the following assumes you only have one bot
    bot_id = r.json()[0]['id']
    return bot_id


class PlotBot:
    def __init__(self):
        self.b_id = 78829
        self.plotted = []
        print(f"[Placer Bot {self.b_id}]: init")

    def post_wall(self, wall):
        self._move_to(wall['wall']['pos']['x'] + 1, wall['wall']['pos']['y'])
        self._orient('left')
        res = requests.post(
            url=f"https://recurse.rctogether.com/api/walls?app_id={ID}&app_secret={SEC}&bot_id={self.b_id}",
            json=wall)
        print(res.json())
        # self.plotted.append(res.json()["id"])  # (wall['wall']['pos']['x'], wall['wall']['pos']['y'],
        self.plotted.append((wall['wall']['pos']['x'], wall['wall']['pos']['y'], res.json()["id"]))
        return res

    # def _place_wall(self, x, y, clr="gray", txt=" "):
    #     self._move_to(x+1, y)
    #     jsn = {"bot_id": self.b_id,
    #            "wall": {
    #                "pos": {
    #                    "x": x,
    #                    "y": y
    #                },
    #                "color": clr,
    #                "wall_text": txt
    #            }}
    #     res = post("", jsn, WALLURL)
    #
    #     self.pegs.append((x, y, res.json()["id"]))
    #     print(f"[Plotter Bot {self.b_id}]: made wall with params x={x}, y={y}, clr={clr}, txt={txt}")

    def _erase_wall(self, x, y, idx):
        j = {"bot_id": self.b_id}
        # self._move_to(x+1, y)
        # self._orient('right')
        delete(idx, j, WALLURL)
        print(f"[Plotter Bot {self.b_id}]: erased wall at x={x}, y={y}")

    def _move_to(self, x, y):
        jsn = {"bot": {"x": x, "y": y}}
        patch(self.b_id, jsn)
        print(f"[Plotter Bot {self.b_id}]: moved to position x={x}, y={y}")

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

    def plot(self, list_ints):
        for i in list_ints:
            plot_int_vertical_base10(i, 71 + i, 108, self.b_id)


    def plot_int_vertical_base10(self, i, x, y0, base=10):
        colours = ["gray", "pink", "orange", "green", "blue", "purple",  "yellow"]

        def plot_digit(i, modulo, x, y):
            (q, r) = divmod(i, modulo)
            if q > 0:
                col = colours[int(math.floor(math.log10(modulo)))]
                wall = {'wall': {'x': x, 'y': y, 'color': col, 'wall_text': str(q)}}
                res = self.post_wall(wall)
                plot_digit(i, modulo*base, x, y+1)  # recursive call
                print(f"update_wall status: {res.status_code}")
            return 0
        # plot walls out of integer i
        plot_digit(i, 1, x, y0)

    def scale_vector(array):
        if array:
            if isinstance(array[0], int) | isinstance(array[0], float):
                if(max(array)) > 20:
                    scale = max(array)/20
                    return [e/scale for e in array]

    def array_dict_to_dict_two_arrays(array_dict):
        key1 = list(array_dict[0].keys())[0]
        key2 = list(array_dict[0].keys())[1]
        twolists = [list(i.values()) for i in array_dict]
        return {key1: twolists[0], key2: twolists[1]}

    #129. 109 is bottomrow position
    # takes dict of two arrays, so call the above before passing to here.
    def plot_named_horizontals(self, dic, x, y, note_text):
        self.clear()
        names_to_write_on_walls = list(dic.values())[0]
        wall_lengths = list(dic.values())[1]
        colours = ["gray", "pink", "orange", "green", "blue", "purple",  "yellow"]

        def plot_one_wall(graffiti, wall_length , x0, y0, col):
            for j in wall_length:
                graffiti_len = len(str(graffiti))
                wall_text = ''  # default
                if j < graffiti_len:
                    wall_text = str(graffiti)[j]
                wall = {'wall': {'pos': {'x': x0 + j, 'y': y0}, 'color': col, 'wall_text': wall_text}}
                res = self.post_wall(wall)

        for k in len(names_to_write_on_walls):
            col = colours[k % len(colours)]
            plot_one_wall(names_to_write_on_walls[k], wall_lengths[k], x, y - k, col)

            # note_text = "Plot of " + str(list(dic.keys())[1]) + " against " + str(list(dic.keys())[0])
            # note = {'note': {'pos': {'x': x - 1, 'y': y}, 'note_text': note_text}}
            # res_note = requests.post(
            #     url=f"https://recurse.rctogether.com/api/notes?app_id={ID}&app_secret={SEC}&bot_id={self.b_id}",
            #     json=note)
            # print(res_note)
# end PlotBot

def delete_bot():
    b_id = get_bot()
    r = requests.delete(url=f"https://recurse.rctogether.com/api/bots/{b_id}?app_id={ID}&app_secret={SEC}")
    print(f"delete status: {r.status_code}")


# this function allows you to decide what to do with message contents
def sub_on_receive(message):
    print("New message received of type {}!".format(message['type']))
    # here you may want to call other functions
    # that send HTTP requests to https://recurse.rctogether.com/api based on the message input

    # the first message you receive will be 'world', which is the status for EVERYTHING in VirtualRC
    # don't print it; it's huge
    if message['type'] == "world":
        init_bot()
        time.sleep(3)
        get_bot()
        time.sleep(3)
        update_bot()
        time.sleep(30)
        delete_bot()


# ==== REST API ================================================================

BOTURL = "https://recurse.rctogether.com/api/bots/"
NOTEURL = "https://recurse.rctogether.com/api/notes/"
WALLURL = "https://recurse.rctogether.com/api/walls/"


def post(id, j, url=BOTURL):
    return requests.post(url+str(id), json=j, auth=(ID, SEC))


def patch(id, j, url=BOTURL):
    return requests.patch(url+str(id), json=j, auth=(ID, SEC))


def delete(id, j=None, url=BOTURL):
    if j is None:
        return requests.delete(url+str(id), auth=(ID, SEC))
    else:
        return requests.delete(url+str(id), json=j, auth=(ID, SEC))

# ==== REST API ================================================================


if __name__ == "__main__":
    import os
    ID = os.getenv('VIRTUALRCID')
    print("id from osgetenv is "+str(ID))
    SEC = os.getenv('VIRTUALRCSEC')
    con = Connection(origin='https://recurse.rctogether.com',
                     url=f'wss://recurse.rctogether.com/cable?app_id={ID}&app_secret={SEC}')
    con.connect()
    # you're connected! but you don't have any messages yet
    # check this to make sure you are connected
    print(con.connected)

    # be careful with your quotation marks!
    sub = Subscription(con, identifier={"channel": "ApiChannel"})

    sub.on_receive(callback=sub_on_receive)

    # this function sends the "command":"subscribe" message to the ApiChannel
    sub.create()
    # you should now be receiving messages! if not, check the following
    print(sub.state)
    # if sub.state is 'pending', you may have downloaded the old version of ActionCableZwei!
    # 'subscription_pending' means that your Connection object is not connected (check con.connected)

    # # this 'unsubscribes' you from the ApiChannel
    # sub.remove()
    #
    # # re-subscribing will send you a new 'world' message
    # sub.create()

    # here are some basic examples for building a bot
    # this bot will appear in the top-left corner of VirtualRC
    bot_info = {
        "bot": {
            "name": "Plotter Bot",
            "emoji": "😊",
            "x": 120,
            "y": 109,
            "direction": "right",
            "can_be_mentioned": False,
        }
    }

    bot_message = {
        "text": "Hello, I am a bot run from plotter.py"
    }

    # successful requests return status code 200
    def init_bot():
        r = requests.post(url=f"https://recurse.rctogether.com/api/bots?app_id={ID}&app_secret={SEC}", json=bot_info)
        print(f"Init status: {r.status_code}")

    # init_bot()
    b_id = get_bot()
    PLOT_BOT = PlotBot()
    # dic = {['one', "sdf sdf sdf ", ""], [5, 3, 5]}
    # PLOT_BOT.plot_named_horizontals(dic, 129,109,"")

    # PLOT_BOT.clear()
    wall = {'wall': {'pos': {'x': 129, 'y': 109}, 'color': "yellow", 'wall_text': '!'}}
    res = PLOT_BOT.post_wall(wall)
    wall = {'wall': {'pos': {'x': 130, 'y': 109}, 'color': "yellow", 'wall_text': '!'}}
    res = PLOT_BOT.post_wall(wall)
    print(PLOT_BOT.plotted)
    PLOT_BOT.file_out()

    PLOT_BOT.clear()

    # note = {'note': {'pos': {'x': 129 - 3, 'y': 109}, 'note_text': "asdf", 'color': "gray"}, 'bot_id': b_id}
    # res = requests.post(
    #     url=f"https://recurse.rctogether.com/api/notes?app_id={ID}&app_secret={SEC}&bot_id={b_id}",
    #     json=note)
    print(res)
