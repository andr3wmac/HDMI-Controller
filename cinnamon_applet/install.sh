# Set the PATH variable in applet.js
echo Setting the applet.js PATH variable..
NEW_LOCATION=${HOME}/.local/share/cinnamon/applets/
NEW_DIR=${NEW_LOCATION}hdmi-controller@andrewmac.ca/
REGEX="s/CHANGEME/${NEW_DIR//\//\\/}/"
sed $REGEX < applet.js > hdmi-controller@andrewmac.ca/applet.js

# COPY FILES TO NEW LOCATION
echo Installing applet..
cp -r hdmi-controller@andrewmac.ca ${NEW_LOCATION}

# DONE!
echo Applet installed.
