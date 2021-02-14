from loguru import logger
import time
import requests
import json
import threading

class APIException(Exception):
    """Raised when there was an error returned from the Chroma API call."""
    pass


def keepalive(chroma_obj):
    # while we're running, if the last API request is more than 5 seconds 
    # old, make a keepalive API request, until the Chroma object's running
    # attribute is False.
    while chroma_obj.running:
        if time.time() - chroma_obj.last_api_request > 5:
            chroma_obj.heartbeat()
        else:
            time.sleep(1)

class Chroma:
    def __init__(self):
        self.running = True
        self.headers = {
            "content-type": "application/json"
        }
        self.uri = None
        self.last_api_request = None
        data = json.load(open('chroma_data_post.json', 'r'))
        response = requests.post("http://localhost:54235/razer/chromasdk", json=data, headers=self.headers)
        self.last_api_request = time.time()
        logger.debug(response)
        logger.debug(response.text)
        if response.status_code == 200:
            data = json.loads(response.text)
            self.uri = data.get('uri')
            self.sessionid = data.get('sessionid')
        else:
            raise APIException("Problem initializing API connection.  Response code: {response.status_code}\nText: {response.text}")


    def __del__(self):
        response = requests.delete(self.uri)
        logger.debug(response)
        logger.debug(response.text)


    def keyboard_post(self, data):
        response = requests.post(self.uri + "/keyboard", json=data, headers=self.headers)
        self.last_api_request = time.time()
        logger.debug(response)
        logger.debug(response.text)
        return response

    def apply_effect(self, effect_id):
        data = {
            "id": f"{effect_id}"
        }
        response = requests.put(self.uri + "/effect", json=data, headers=self.headers)
        self.last_api_request = time.time()
        logger.debug(f"Response: {response}")
        return response

    def precreate_keyboard_effect(self, effect, data):
        if effect == "CHROMA_NONE":
            d = {"effect": effect}
        elif effect == "CHROMA_CUSTOM":
            d = {"effect": effect, "param": data}
        elif effect == "CHROMA_STATIC":
            color = {"color": data}
            d = {"effect": effect, "param": color}
        elif effect == "CHROMA_CUSTOM_KEY":
            d = {"effect": effect, "param": data}
        logger.debug(d )
        response = self.keyboard_post(d)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data.get('error') is None:
                effectid = data.get('id')
            else:
                raise APIException("Error precreating keyboard effect.\nResponse: {response.text}")
        else:
            raise APIException(f"Status code not 200 - Status code: {response.status_code}\nMessage: {response.text}")
        return effectid

    def create_static_effect(self, color):
        return self.precreate_keyboard_effect(effect="CHROMA_STATIC", data=color)

    def get_color(self, color_name):
        # Color in this world, is the BGR color in Hex 
        colormap = {
            "red": 0x0000FF,
            "green": 0x00FF00,
            "blue": 0xFF0000,
            "black": 0x000000
        }
        return colormap.get(color_name)


    def heartbeat(self):
        response = requests.put(self.uri + "/heartbeat", json={}, headers=self.headers)
        self.last_api_request = time.time()
        logger.debug(response)
        logger.debug(response.text)

    def shutdown(self):
        self.running = False



def flashy_green_red_blue_keyboard(c):
    times = 10
    red_effect = c.create_static_effect(c.get_color('red'))
    green_effect = c.create_static_effect(c.get_color('green'))
    blue_effect = c.create_static_effect(c.get_color('blue'))
    
    for _ in range(1):
        #effect_id = create_static_effect(65280) # Green
        time.sleep(3)
        for x in range(10):
            c.apply_effect(red_effect)
            time.sleep(.1)
            c.apply_effect(green_effect)
            time.sleep(.1)
            c.apply_effect(blue_effect)
            time.sleep(.1)
        time.sleep(20)
        for x in range(10):
            c.apply_effect(red_effect)
            time.sleep(.1)
            c.apply_effect(green_effect)
            time.sleep(.1)
            c.apply_effect(blue_effect)
            time.sleep(.1)
        
    
# To program keyboard effects, We program 21 columns, 6 rows, and give each
# row a Chroma color, or a 0 to indicate "off".
# Let's try making "every other key" green.

def create_checkerboard_keyboard(chroma_obj):
    rows = 6
    cols = 22
    data = []
    keys = []
    d = {"key": keys, "color": data}
    for x in range(rows):
        this = []
        data.append(this)
        that = []
        keys.append(that)
        for y in range(cols):
            if y % 2 == 0:
                this.append(chroma_obj.get_color('green')) # green
            else:
                this.append(chroma_obj.get_color('red')) # red
            if y % 3 != 0:
                that.append(0x01000000)
            else:
                that.append(chroma_obj.get_color('black'))
    effect = chroma_obj.precreate_keyboard_effect("CHROMA_CUSTOM_KEY", d)
    time.sleep(2)
    chroma_obj.apply_effect(effect)


if __name__ == "__main__":
    # create a chroma obj.
    c = Chroma()
    # spinoff a thread to keep our Chroma object alive.
    keepalive_thread = threading.Thread(target=keepalive, args=(c,))
    keepalive_thread.start()
    try:
        create_checkerboard_keyboard(c)
        #flashy_green_red_blue_keyboard(c)
    except KeyboardInterrupt:
        pass
    time.sleep(10)
    c.shutdown()
    keepalive_thread.join()
    del(c)
    
    #effect = create_checkerboard_keyboard()
    #time.sleep(2)
    #apply_effect(effect)
