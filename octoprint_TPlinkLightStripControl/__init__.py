# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin
import asyncio
import kasa
from kasa import SmartStrip
import threading
import time
import flask
from octoprint.events import Events

class TplinklightstripcontrolPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.ShutdownPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.EventHandlerPlugin
):
    bConnected = False
    MonitoringThread = None
    bShouldUpdate = True
    strip = None
    bLightStripOn = False
    bLightStripOn_old = False
    bChangeState = False
    bStateRequested = False

    def get_api_commands(self):
        return dict(
            turnLEDOn=["parameter"],
            getState=[]
        )

    async def async_func(self):
        await self.strip.update()

    def on_api_command(self, command, data):

        if command == "turnLEDOn":
            self.bStateRequested = data.get("parameter")
            self.bChangeState = True
        elif command == "getState":
            self._logger.info("PSU state query")
            return flask.jsonify(isLEDStripOn=self.bLightStripOn)

    async def toggle_LED_strip(self, bState):
        if(bState):
            await self.strip.children[1].turn_on()
        else:
            await self.strip.children[1].turn_off()

    def on_api_get(self, request):
        return self.on_api_command("getState", [])

    async def thread_function(self):
        while(self.bShouldUpdate):
            try:
                await self.strip.update()

                if (self.bChangeState):
                    self.bChangeState = False
                    await self.toggle_LED_strip(self.bStateRequested)

                await self.strip.update()

                self.bLightStripOn = self.strip.children[1].is_on

                if (self.bLightStripOn != self.bLightStripOn_old):
                    self._plugin_manager.send_plugin_message(self._identifier, dict(isLEDStripOn=self.bLightStripOn))

                self.bLightStripOn_old = self.bLightStripOn

                self.bConnected = True
            except:
                self.bConnected = True

            await asyncio.sleep(1)

    def on_startup(self, *args, **kwargs):
        self.bLightStripOn = False
        self.bLightStripOn_old = False

    def on_after_startup(self):
        try:
            self.strip = SmartStrip("192.168.1.9")
            self.bConnected = True
        except:
            self._logger.info("Connection Failed!")
            self.bConnected = False

        self._logger.info("Hello World!")

        self.MonitoringThread = threading.Thread(target=asyncio.run, args=(self.thread_function(), ))
        self.MonitoringThread.daemon = True
        self.MonitoringThread.start()

    ##~~ SettingsPlugin mixin

    def on_shutdown(self):
        self.bShouldUpdate = False
        self.MonitoringThread.join()

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/TPlinkLightStripControl.js"],
            "css": ["css/TPlinkLightStripControl.css"],
            "less": ["less/TPlinkLightStripControl.less"]
        }

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "TPlinkLightStripControl": {
                "displayName": "Tplinklightstripcontrol Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "vlatomik",
                "repo": "OctoPrint-Tplinklightstripcontrol",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/vlatomik/OctoPrint-Tplinklightstripcontrol/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "Tplinklightstripcontrol Plugin"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = TplinklightstripcontrolPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
