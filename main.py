# Lux32 ESP32 Lighting Controller
# Copyright 2023, Lukas Severinghaus
# Released under the GPL license

import neopixel
import machine
from secrets import SECRET_BROKER_IP, SECRET_SSID, SECRET_PASS, DEVICE_NAME
import uasyncio as asyncio
from mqtt_async import MQTTClient, config
import ugit


UPDATE_TOPIC = DEVICE_NAME+"/update"
OFF_TOPIC = DEVICE_NAME+"/off"
CMD_TOPIC = DEVICE_NAME+"/cmd"

segment_order = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 6, 30]

def set_all_color(r, g, b):
    global pixels
    for i in range(len(pixels)):
        pixels[i] = (r, g, b)

def set_segment(seg, r, g, b):
    global segment_order
    start_index = segment_order.index(seg)
    for i in range(8):
        pixels[(start_index)*8 + i] = (int(r), int(g), int(b))

left_right_seg = [
    [18, 19, 22, 23],
    [17, 20, 24],
    [14, 15, 21, 26, 25, 27],
    [13, 16, 30, 28],
    [12, 10, 11, 5, 6, 29],
    [9, 4, 1],
    [8, 7, 3, 2]
]

top_down_seg = [
    [13],
    [14, 12],
    [17, 9],
    [18, 15, 10, 8],
    [16],
    [19, 21, 11, 7],
    [20, 4],
    [22, 26, 5, 3],
    [30],
    [23, 25, 6, 2],
    [24, 1],
    [27, 29],
    [28]
]

def hsv_to_rgb(h, s, v):
    h = h % 360
    # https://www.had2know.org/technology/hsv-rgb-conversion-formula-calculator.html
    M = 255 * v
    m = M * (1-s)
    z = (M-m) * (1-abs((h/60)%2 - 1))

    ah = h
    r = 0
    g = 0
    b = 0

    if ah < 60:
        r = M
        g = z+m
        b = m
    elif 60 <= ah < 120:
        r = z+m
        g = M
        b = m
    elif 120 <= ah < 180:
        r=m
        g = M
        b = z+m
    elif 180 <= ah < 240:
        r = m
        g = z+m
        b = M
    elif 240 <= ah < 300:
        r = z+m
        g = m
        b = M
    elif 300 <= ah < 360:
        r = M
        g = m
        b = z+m

    return (r, g, b)

async def logic():
    global pixels
    VERT_TRANS = 1
    HOR_TRANS = 2
    mode = 1
    i = 0
    hue = 20
    while 'pixels' not in globals():
        await asyncio.sleep(0.1)
    while True:
        print("Logic")
        color = hsv_to_rgb(hue, 1, 1)
        print("Color", color, hue)
        if mode == VERT_TRANS:
            if i >= len(top_down_seg):
                i = 0
                hue = hue + 10
                print("Looping around")
            print("Setting segment: ", i)
            for seg in top_down_seg[i]:
                set_segment(seg, color[0], color[1], color[2])

        elif mode == HOR_TRANS:
            if i >= len(left_right_seg):
                i = 0
                hue = hue + 10
                print("Looping around")
            print("Setting segment: ", i)
            for seg in left_right_seg[i]:
                set_segment(seg, color[0], color[1], color[2])

        i = i + 1
        await asyncio.sleep(0.05)

async def canvas():
    global pixels
    n = 240
    p = machine.Pin(13)

    pixels = neopixel.NeoPixel(p, n)

    while True:
        pixels.write()
        await asyncio.sleep(0.05)

def mqtt_callback(topic, msg, retained, qos):
    global UPDATE_TOPIC
    topic = topic.decode()
    if topic == UPDATE_TOPIC:
        print("Updating")
        ugit.pull_all()
    elif topic == OFF_TOPIC:
        print("Off")
    elif topic == CMD_TOPIC:
        msg = msg.decode()
        print("Cmd: ", msg)


async def mqtt(client):
    await client.connect()

if __name__ == "__main__":
    config.server = SECRET_BROKER_IP
    config.ssid = SECRET_SSID
    config.wifi_pw = SECRET_PASS
    config.subs_cb = mqtt_callback

    client = MQTTClient(config)

    loop = asyncio.get_event_loop()

    loop.create_task(mqtt(client))
    loop.create_task(logic())
    loop.create_task(canvas())

    loop.run_forever()