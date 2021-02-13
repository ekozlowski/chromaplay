from loguru import logger
import time
import requests
import json


class APIException(Exception):
    """Raised when there was an error returned from the Chroma API call."""
    pass

headers = {
    "content-type": "application/json"
}

def initialize():
    data = json.load(open('./chrome_data_post.json', 'r'))
    response = requests.post("http://localhost:54235/razer/chromasdk", json=data, headers=headers)
    log.debug(response)
    log.debug(response.text)
    if response.status_code == 200:
        data = json.loads(response.text)
        uri = data.get('uri')
        sessionid = data.get('sessionid')
    else:
        raise APIException("Problem initializing API connection.  Response code: {response.status_code}\nText: {response.text}")
    return uri

uri = initialize()


def precreate_keyboard_effect(effect, data):
    if effect == "CHROMA_NONE":
        d = {"effect": effect}
    elif effect == "CHROMA_CUSTOM":
        d = {"effect": effect, "param": data}
    elif effect == "CHROMA_STATIC":
        color = {"color": data}
        d = {"effect": effect, "param": color}
    elif effect == "CHROMA_CUSTOM_KEY":
        d = {"effect": effect, "param": data}
    logger.debug(d)
    response = requests.post(uri + "/keyboard", json=d, headers=headers)
    logger.debug(response)
    logger.debug(response.text)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data.get('error') is None:
            effectid = data.get('id')
        else:
            raise APIException("Error precreating keyboard effect.\nResponse: {response.text}")
    else:
        raise APIException(f"Status code not 200 - Status code: {response.status_code}\nMessage: {response.text}")
    return effectid

def apply_effect(effect_id):
    data = {
        "id": f"{effectid}"
    }
    response = requests.put(uri + "/effect", json=data, headers=headers)
    logger.debug(f"Response: {response}")


def create_static_effect(color):
    return precreate_keyboard_effect(effect="CHROMA_STATIC", data=color)

def apply_effect(effect_id):
    data = {
        "id": f"{effect_id}"
    }
    response = requests.put(uri + "/effect", json=data, headers=headers)
    logger.debug(response)
    logger.debug(response.text)


def get_color(color_name):
    # Color in this world, is the BGR color in Hex 
    colormap = {
        "red": 0x0000FF,
        "green": 0x00FF00,
        "blue": 0xFF0000,
        "black": 0x000000
    }
    return colormap.get(color_name)


def heartbeat():
    response = requests.put(uri + "/heartbeat", json={}, headers=headers)
    logger.debug(response)
    logger.debug(response.text)
    time.sleep(.1)

def flashy_green_red_blue_keyboard():
    times = 10
    red_id = create_static_effect(get_color('red')) # Red
    green_id = create_static_effect(get_color('green')) # Green
    blue_id = create_static_effect(get_color('blue')) # Blue

    for _ in range(1):
        #effect_id = create_static_effect(65280) # Green
        time.sleep(3)
        
        while(True):
            apply_effect(red_id)
            time.sleep(.1)
            apply_effect(green_id)
            time.sleep(.1)
            apply_effect(blue_id)
            time.sleep(.1)

# To program keyboard effects, We program 21 columns, 6 rows, and give each
# row a Chroma color, or a 0 to indicate "off".
# Let's try making "every other key" green.

def create_checkerboard_keyboard():
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
                this.append(get_color('green')) # green
            else:
                this.append(get_color('red')) # red
            if y % 3 == 0:
                that.append(get_color('black'))
            else:
                that.append(get_color('black'))

    print(data)
    return precreate_keyboard_effect("CHROMA_CUSTOM_KEY", d)



if __name__ == "__main__":
    effect = create_checkerboard_keyboard()
    time.sleep(2)
    apply_effect(effect)



