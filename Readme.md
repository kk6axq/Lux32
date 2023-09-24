# Lux32: ESP32 Lighting Controller
Lux32 is an ESP32 based lighting controller for my second generation hexagon lights.

It uses 240 WS2812B addressable LEDs, with 8 per segment in a grid of 7 hexagons.

This code runs on the onboard ESP32, and using `ugit` it auto updates from here as well.

# Operation

The lights are designed to take commands from a local MQTT broker. This makes it easy to integrate with my other smart devices, and I control it from my phone with an MQTT dashboard app.


# License
Lux32 is licensed under the GPL license, see `License.md`.
`ugit.py` is from [turfptax/ugit](https://github.com/turfptax/ugit) and is also licensed under the GPL license.