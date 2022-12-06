/*
 * View model for OctoPrint-Tplinklightstripcontrol
 *
 * Author: Tomas Vlach
 * License: AGPLv3
 */

$(function() {
    function TplinklightstripcontrolViewModel(parameters) {
        var self = this;
        self.isLEDStripOn = ko.observable(undefined);

        self.LED_indicator = $("#tplinklightstripcontrol_indicator");

        console.log("Hello world!1");

        self.onStartup = function () {
            self.isLEDStripOn.subscribe(function() {
                if (self.isLEDStripOn()) {
                    self.LED_indicator.removeClass("off").addClass("on");
                } else {
                    self.LED_indicator.removeClass("on").addClass("off");
                }   
            });

            $.ajax({
                url: API_BASEURL + "plugin/TPlinkLightStripControl",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "getState"
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {
                self.isLEDStripOn(data.isLEDStripOn);
            });

        }

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "TPlinkLightStripControl") {
                return;
            }

            if (data.isLEDStripOn !== undefined) {
                self.isLEDStripOn(data.isLEDStripOn);
            }
        };

        self.toggleLEDStrip = function() {
            console.log("Hello world!3");
            self.sendToggleCommand();
        };

        self.queryState = function() {
            $.ajax({
                url: API_BASEURL + "plugin/TPlinkLightStripControl",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "getState"
                }),
                contentType: "application/json; charset=UTF-8"
            }).done(function(data) {
                self.isLEDStripOn(data.isLEDStripOn);
            });
        }

        self.sendToggleCommand= function() {
            $.ajax({
                url: API_BASEURL + "plugin/TPlinkLightStripControl",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    command: "turnLEDOn",
                    parameter: !self.isLEDStripOn()
                }),
                contentType: "application/json; charset=UTF-8"
            })

            console.log(!self.isLEDStripOn())
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: TplinklightstripcontrolViewModel,
        dependencies: [],
        elements: ["#navbar_plugin_TPlinkLightStripControl"]
    });
});