const PATH = "/usr/share/cinnamon/applets/hdmi-controller@cinnamon.org/";

const Main = imports.ui.main;
const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const GLib = imports.gi.GLib;
const Gettext = imports.gettext.domain('cinnamon-applets');
const _ = Gettext.gettext;

function MyMenu(launcher, orientation) {
    this._init(launcher, orientation);
}

MyMenu.prototype = {
    __proto__: PopupMenu.PopupMenu.prototype,
    
    _init: function(launcher, orientation) {
        this._launcher = launcher;        
                
        PopupMenu.PopupMenu.prototype._init.call(this, launcher.actor, 0.0, orientation, 0);
        Main.uiGroup.add_actor(this.actor);
        this.actor.hide();            
    }
}

function MyApplet(orientation) {
    this._init(orientation);
}

MyApplet.prototype = {
    __proto__: Applet.IconApplet.prototype,

    _init: function(orientation) {        
        Applet.IconApplet.prototype._init.call(this, orientation);
        
        try {        
            this.set_applet_icon_name("monitor");
            this.set_applet_tooltip(_("HDMI Controller"));
            
            this.menuManager = new PopupMenu.PopupMenuManager(this);
            this.menu = new MyMenu(this, orientation);
            this.menuManager.addMenu(this.menu);            
                                
            this.menu.addAction(_("Enable HDMI"), function() {
                GLib.spawn_command_line_async('python ' + PATH + 'hdmi_controller.py --enable');
            });
            this.menu.addAction(_("Disable HDMI"), function() {
                GLib.spawn_command_line_async('python ' + PATH + 'hdmi_controller.py --disable');
            });
            this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
            //this.menu.addSettingsAction(_("HDMI Settings"), 'gnome-universal-access-panel.desktop');
            this.menu.addAction(_("Settings"), function() {
                GLib.spawn_command_line_async('python ' + PATH + 'hdmi_controller.py');
            });
        }
        catch (e) {
            global.logError(e);
        }
    },
    
    on_applet_clicked: function(event) {
        this.menu.toggle();        
    },
};

function main(metadata, orientation) {  
    let myApplet = new MyApplet(orientation);
    return myApplet;      
}
