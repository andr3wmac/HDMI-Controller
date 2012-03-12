
HDMI-Controller v0.9.5

Copyright 2012, Andrew Mac
  http://www.andrewmac.ca
Licensed under GPL v3.
  See LICENSE.txt

------------------------------
 SETUP
------------------------------

For the controller to function you need to adjust a few values in hdmi_controller.cfg:

    screen = LVDS1
    screen_resolution = 1440x900 @ 60hz
    hdmi = HDMI1
    pulse_default_sink = alsa_output.pci-0000_00_1b.0.analog-stereo
    hdmi_audio_device = hw:0,3

Open a terminal and run 'xrandr' and it will show you a list, for instance:

    LVDS1 connected 1440x900+0+0 (normal left inverted right x axis y axis) 303mm x 190mm
       1440x900       59.9*+   59.9  
       1360x768       59.8     60.0  
       1152x864       60.0  
       1024x768       60.0  
       800x600        60.3     56.2  
       640x480        59.9  
    HDMI1 disconnected (normal left inverted right x axis y axis)

The resolution with the * next to it is the one you're currently on. So fill in screen, screen_resolution, and hdmi values. I rounded to 60hz, you can put 59.9hz if you wish.

The next part is a little trickier, you need to find your default pulse audio sink. Run the command 'pacmd list-sinks'. This will list all the sinks, in my case there is only one, the top part of the output looks like this:

  * index: 0
	name: <alsa_output.pci-0000_00_1b.0.analog-stereo>
	driver: <module-alsa-card.c>
	flags: HARDWARE HW_MUTE_CTRL HW_VOLUME_CTRL DECIBEL_VOLUME LATENCY DYNAMIC_LATENCY
	state: RUNNING

So my pulse_default_sink = alsa_output.pci-0000_00_1b.0.analog-stereo
This defines the sink the the controller will switch back to when you disable HDMI settings.

The last value to fill in, hdmi_audio_device should be simple. Run the command 'aplay -l' and it will give you a list of audio devices. Each device will be formatted as such:

    card 0: Intel [HDA Intel], device 0: ALC262 Analog [ALC262 Analog]
      Subdevices: 0/1
      Subdevice #0: subdevice #0

Note the card number 0 and the device number 0. This would be referred to as hw:0,0. If your HDMI audio device is on card 0 and is device 3 like mine you would set hdmi_audio_device = hw:0,3

Now just run the application and when you click 'Apply HDMI Settings' it should clone your computer screen on the HDMI out, and the audio should now be going over that as well. When you click the disable button it will revert back to your original settings.


