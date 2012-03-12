"""
 * HDMI-Controller v0.9.5
 *
 * Copyright 2012, Andrew Mac
 * http://www.andrewmac.ca
 * Licensed under GPL v3.
 * See LICENSE.txt
"""

import pygtk, sys, ConfigParser, commands, logging, os
pygtk.require('2.0')
import gtk

# this could be launched from anywhere.
os.chdir(os.path.dirname(__file__))

class HDMIController:
    def saveAndApply(self, widget, data=None):
        self.applySettings()
        self.saveConfig()
    
    def applySettings(self):
        # Parse selected resolution.
        #model = self.res_combo.get_model()
        #index = self.res_combo.get_active()
        #res_line = model[index][0]
        #res = self.parseResolution(res_line)

        # load settings.
        res = self.parseResolution(self.res_list[self.config.getint("user_settings", "res_index")])
        set_primary = self.config.getboolean("user_settings", "hdmi_primary")
        active_audio = self.config.getboolean("user_settings", "hdmi_audio")

        # Setup HDMI
        mode_name = self.addMode(self.hdmi_name, res)
        self.displayConfig(self, self.hdmi_name, mode = mode_name, pos = "0x0", primary = set_primary)

        # Scale the screen
        h_scale = (float)(res[0])/(float)(self.screen_res[0])
        v_scale = (float)(res[1])/(float)(self.screen_res[1])
        self.displayConfig(self, self.screen_name, scale = str(h_scale) + "x" + str(v_scale))

        # Turn on HDMI Audio
        if ( active_audio ):
            self.createSink(self.hdmi_audio, "HDMI")
            self.setDefaultSink("HDMI")

    def disableSettings(self, widget, data=None):
        # disable HDMI
        self.cmd("xrandr --output " + self.hdmi_name + " --off")

        # set the screen to default settings.
        mode_name = self.addMode(self.screen_name, self.screen_res)
        self.displayConfig(self.screen_name, mode = mode_name, scale = "1x1", primary = True)

        # set pulse back to default audio device
        self.setDefaultSink(self.default_sink)

    def deleteEvent(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def parseResolution(self, res_line):
        # Takes the format '1920x1080 @ 60hz (16:9)'
        # and returns [1920, 1080, 60]
        args = res_line.split(" ")
        res = args[0].split("x")        
        hz = args[2][:-2]
        return [int(res[0]), int(res[1]), int(hz)]

    def cmd(self, command):
        result = commands.getoutput(command)
        self.log("Executed command '" + command + "' Result: " + result) 
        return result

    def log(msg):
        if ( self.logger ):
            self.logger.debug(msg)

    def addMode(self, display, res):
        # Get mode line.
        result = self.cmd("cvt " + str(res[0]) + " " + str(res[1]) + " " + str(res[2])).split("\n")
        mode_line = result[1][9:]
        mode_name = mode_line.split(" ")[0].replace("\"", "")

        # Delete mode to be safe, create new mode
        # then add to the display.
        #self.cmd("xrandr --rmmode " + mode_name)
        self.cmd("xrandr --newmode " + mode_line)
        self.cmd("xrandr --addmode " + display + " " + mode_name)
        return mode_name

    def displayConfig(self, display_name, mode = None, pos = None, primary = False, scale = None):
        cfg_line = "xrandr --output " + display_name
        if ( mode ): cfg_line += " --mode " + mode
        if ( pos ): cfg_line += " --pos " + mode
        if ( primary ): cfg_line += " --primary"
        if ( scale ): cfg_line += " --scale " + scale

        return self.cmd(cfg_line)

    def createSink(self, device, sink_name):
        self.cmd("pacmd load-module module-alsa-sink device=" + device + " sink_name=" + sink_name)

    def setDefaultSink(self, sink):
        self.cmd("pacmd set-default-sink " + sink)

    def loadConfig(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read("hdmi_controller.cfg")
        
        # load app settings
        self.hdmi_name = self.config.get("app_settings", "hdmi")
        self.hdmi_audio = self.config.get("app_settings", "hdmi_audio_device")
        self.default_sink = self.config.get("app_settings", "pulse_default_sink")
        self.screen_name = self.config.get("app_settings", "screen")
        self.screen_res = self.parseResolution(self.config.get("app_settings", "screen_resolution"))
        self.res_list = self.config.get("app_settings", "hdmi_resolutions").split(",")

    def saveConfig(self):
        index = self.res_combo.get_active()
        self.config.set("user_settings", "res_index", str(index))
        self.config.set("user_settings", "hdmi_primary", str(self.primary_check.get_active()))
        self.config.set("user_settings", "hdmi_audio", str(self.audio_check.get_active()))
        with open('hdmi_controller.cfg', 'wb') as configfile:
            self.config.write(configfile)

    def __init__(self):
        # setup logging.
        try:
            hdlr = logging.FileHandler('hdmi_controller.log')
            formatter = logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
            hdlr.setFormatter(formatter)
            self.logger = logging.getLogger('hdmi_controller')
            self.logger.addHandler(hdlr) 
            self.logger.setLevel(logging.DEBUG)
        except:
            pass

        # Load configuration.
        self.loadConfig()

        # Process any args.
        for arg in sys.argv:
            if ( arg == "-enable" or arg == "--enable" ):
                self.applySettings()
                sys.exit(0)
                
            if ( arg == "-disable" or arg == "--disable" ):
                self.disableSettings(None)
                sys.exit(0)

        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("HDMI Controller")
        self.window.connect("delete_event", self.deleteEvent)
        self.window.set_border_width(20)
        self.window.set_icon_from_file("hdmi_logo.png")
        vbox = gtk.VBox(False, 2)
        self.window.add(vbox)

        # HDMI logo, illegal?
        logo = gtk.Image()
        logo.set_from_file("hdmi_logo.png")
        vbox.pack_start(logo, True, True, 2)

        # Resolution combo box.
        self.res_combo = gtk.combo_box_new_text()
        vbox.pack_start(self.res_combo, True, True, 2)

        # HDMI as Primary Display
        self.primary_check = gtk.CheckButton("Make HDMI Primary Display")
        vbox.pack_start(self.primary_check, True, True, 2)

        # Audio over HDMI
        self.audio_check = gtk.CheckButton("Enable Audio over HDMI")
        vbox.pack_start(self.audio_check, True, True, 2)

        # Button to Apply/Save settings.
        button = gtk.Button("Apply and Save Settings")
        button.connect("clicked", self.saveAndApply)
        vbox.pack_start(button, True, True, 2)

        # Disable any changes we have active.
        button = gtk.Button("Disable HDMI Settings")
        button.connect("clicked", self.disableSettings)
        vbox.pack_start(button, True, True, 2)

         # load user settings and show window.
        for res in self.res_list:
            self.res_combo.append_text(res)
        self.res_combo.set_active(self.config.getint("user_settings", "res_index"))
        self.primary_check.set_active(self.config.getboolean("user_settings", "hdmi_primary"))
        self.audio_check.set_active(self.config.getboolean("user_settings", "hdmi_audio"))
        self.window.show_all()

def main():
    gtk.main()
    return 0       

if __name__ == "__main__":
    HDMIController()
    main()
