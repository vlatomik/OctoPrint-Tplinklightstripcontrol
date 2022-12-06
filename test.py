import kasa
from kasa import SmartStrip
import asyncio

strip = SmartStrip("192.168.1.9")
asyncio.run(strip.update())
asyncio.run(strip.children[1].turn_on())
