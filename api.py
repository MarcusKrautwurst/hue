# coding=utf-8
__author__ = "marcus.krautwurst"
__version__ = 0.1

import json
import urllib2
import urllib
import collections
import math


class Bridge(object):
    """
    This object is an instance of your bridge. It holds a reference to all the lights
    """
    adress = None
    ip = None
    lights = []
    groups = []
    user = None


    def __init__(self, adress=None):
        pass

    def createuser(self, user, description="python_api"):
        """
        Attempts to create a new user
        """
        userexist = None
        success = False

        check = self.request('%s/api/%s' % (self.adress, user), 'GET')

        try:
            check[0]["error"]["type"] == 1
        except KeyError:
            userexist = True

        # If the user doesnt exist, we create him here
        if not userexist:
            dataToJson = json.dumps({"devicetype": description, "username": user})
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request('%s/api' % self.adress, data=dataToJson)
            response = opener.open(request)
            response = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
            try:
                response[0]["error"]["type"] == 101
                print 'To create this user, press the link button and run this function again within 30 seconds'

            except KeyError:
                try:
                    response[0]["success"]
                    self.user = user
                    success = True
                    print "User: '%s' successfully created" % user
                except KeyError:
                    print 'There was an error creating this user'
                    success = False
        else:
            print "The user already exists"

        return success

    def findbridge(self):
        """
        Attempts to find a bridge on your local network
        """
        find = json.load(urllib2.urlopen('http://www.meethue.com/api/nupnp'))
        if len(find) > 0:
            try:
                self.ip = find[0]["internalipaddress"]
                self.adress = "http://%s" % self.ip
                print 'Found bridge at %s' % find[0]["internalipaddress"]
                return True

            except KeyError:
                print "No bridge found"
                return False
        else:
            print "No bridge found"
            return False

    def set_manual(self, ip):
        """
        Let's you manually define the bridge ip
        """
        self.ip = ip
        self.adress = "http://%s" % ip

    def getlights(self):
        """
        Receive all the lights
        """
        if self.user != None:
            readLights = self.request('%s/api/%s/lights' % (self.adress, self.user), 'GET')

            for light in readLights:
                # Here we create the light instance
                mylight = Light(self)

                mylight.name = readLights[light]["name"]
                mylight.id = int(light)
                self.lights.append(mylight)

            return True
        else:
            print "No valid user, please create one or use an existing one"
            return False

    def getschedules(self):
        """
        Receives all schedules from the bridge and populates them into self.schedules
        """
        if self.user != None:
            self.schedules = Schedules(self)
            schedules = self.request('%s/api/%s/schedules' % (self.adress, self.user), 'GET')
            if len(schedules)>0:
                for each in range(len(schedules)):
                    try:
                        myschedule = schedules[str(each+1)]
                        newschedule = Schedule(myschedule["name"],myschedule["time"][0:9],myschedule["time"][10:-1])
                        newschedule.command = myschedule["command"]

                        self.schedules.append(newschedule)
                    except KeyError:
                        print "Error receiving schedules from the bridge"
                        pass
            else:
                return False
        else:
            print "No valid user, please create one or use an existing one"
            return False

    def request(self, url, method, data=None):
        """
        Sends a request to the bridge
        url: the url that's being added to the base url
        method: GET, POST, PUT
        data: A dictionary (for GET its not needed)
        """
        if isinstance(data, dict) and method is not 'GET':
            data = json.dumps(data)
            if method == 'PUT':
                opener = urllib2.build_opener(urllib2.HTTPHandler)
                request = urllib2.Request("%s/api/%s/%s" % (self.adress, self.user, url), data=data)
                request.add_header("Content-Type", "application/json")
                request.get_method = lambda: 'PUT'
                connection = opener.open(request)
            else:
                header = {"Content-Type": "application/json"}
                try:
                    request = urllib2.Request('%s/api/%s/%s' % (self.adress, self.user, url), data, header)
                    connection = urllib2.urlopen(request)
                except:
                    pass
        else:
            request = urllib2.Request(url)
            connection = urllib2.urlopen(request)
            
        response = connection.read()
        connection.close()
        
        try:
            content = json.loads(response)
        except:
            content = response
        return content

    def getconfig(self):
        """
        Returns a dictionary with all system settings of your bridge, you can also access them individually like this:

        proxyport	uint16	Port of the proxy being used by the bridge. If set to 0 then a proxy is not being used.
        UTC	string	Current time stored on the bridge.
        name	string 4..16	Name of the bridge. This is also its uPnP name, so will reflect the actual uPnP name after any conflicts have been resolved.
        swupdate	object	Contains information related to software updates.
        whitelist	object	An array of whitelisted user IDs.
        swversion	string	Software version of the bridge.
        proxyaddress	string 0..40	IP Address of the proxy server being used. A value of “none” indicates no proxy.
        mac	string	MAC address of the bridge.
        linkbutton	bool	Indicates whether the link button has been pressed within the last 30 seconds.
        ipaddress	string	IP address of the bridge.
        netmask	string	Network mask of the bridge.
        gateway	string	Gateway IP address of the bridge.
        dhcp	bool	Whether the IP address of the bridge is obtained with DHCP.
        portalservices	bool	This indicates whether the bridge is registered to synchronize data with a portal account.
        """
        return mybridge.request("%s/api/%s/config" % (mybridge.adress,mybridge.user),'GET')


class Group(object):
    """
    This is a group of lights
    """
    #@TODO: Implement groups
    name = None
    id = None
    lights = []
    lastcommand = None

    def __init__(self):
        pass


class Light(object):
    """
    This is a light, make it shine
    """

    # Private properties
    _color = (255, 255, 255)
    _saturation = 255
    _intensity = 0
    _name = ""
    _on = None
    _transitiontime = 10
    _loop = False


    # Public properties
    bridge = None
    id = 0

    # Color presets
    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "turquoise": (0, 255, 255)
    }

    def __init__(self, bridge):
        self.bridge = bridge
        pass

    def __repr__(self):
        return "Light: ID: %s NAME: %s" % (self.id, self._name)


    def _RGBToXY(self, r, g, b):
        """
        Private method
        Converts rgb color into xy values for setting the color
        This function is extracted from Tim Rijckaert
        http://stackoverflow.com/questions/22564187/rgb-to-philips-hue-hsb
        """

        normcol = [r / 255, g / 255, b / 255]

        if normcol[0] > 0.04045:
            red = math.pow((normcol[0] + 0.055 / (1.0 + 0.055)), 2.4)
        else:
            red = normcol[0] / 12.92

        if normcol[1] > 0.04045:
            green = math.pow((normcol[1] + 0.055 / (1.0 + 0.055)), 2.4)
        else:
            green = normcol[1] / 12.92

        if normcol[2] > 0.04045:
            blue = math.pow((normcol[2] + 0.055 / (1.0 + 0.055)), 2.4)
        else:
            blue = normcol[2] / 12.92

        red = normcol[0]
        green = normcol[1]
        blue = normcol[2]

        x = red * 0.649926 + green * 0.103455 + blue * 0.197109
        y = red * 0.234327 + green * 0.743075 + blue * 0.022598
        z = red * 0.0000000 + green * 0.053077 + blue * 1.035763

        newX = x / (x + y + z)
        newY = y / (x + y + z)

        return (newX, newY)

    @property
    def name(self):
        """
        Returns the lights name
        """
        return self._name


    @name.setter
    def name(self, value):
        """
        Sets the lights name
        """
        value = str(value)
        if isinstance(value, str):
            # TODO Setting the name on a light doesnt work
            request = self.bridge.request("lights/%s/state" % self.id, 'PUT', {"name": value})
            self._name = value

    @property
    def on(self):
        """
        Returns if the light is on or not
        """
        return self._on

    @on.setter
    def on(self, value):
        """
        Turns the light on or off
        Type: bool
        """
        self.bridge.request("lights/%s/state" % self.id, 'PUT', {"on": value})
        self._on = value


    @property
    def color(self):
        """
        Gets the lights color
        """
        return self._color

    @color.setter
    def color(self, col):
        """
        Sets the lights color
        Example: (255,0,0) for red
        Alternatively you can also use the local dict colors with presets
        Example: self.colors["red"]
        """
        color = self._RGBToXY(col[0], col[1], col[2])
        self.bridge.request("lights/%s/state" % self.id, 'PUT', {"xy": color})

        self._color = col
        pass

    @property
    def saturation(self):
        """
        Gets the lights saturation
        """
        return self._saturation

    @saturation.setter
    def saturation(self, value):
        """
        Sets the lights saturation
        Range: 0-255
        """
        self.bridge.request("lights/%s/state" % self.id, 'PUT', {"sat": value})
        self._saturation = value

    @property
    def intensity(self):
        """
        Gets the lights intensity
        """
        return self._intensity

    @intensity.setter
    def intensity(self, value):
        """
        Sets the lights intensity
        Range: 0.0 <=> 1.0
        """
        if value < 0.001:
            value = 0.001
        elif value > 1.0:
            value = 1.0

        # Remaps value internally from 0-1 to 0-255 (the range the bridge accepts)
        #TODO: Test this more, can it fail?
        remap = int(round((value / 1.0) * 255, 0))

        self.bridge.request("lights/%s/state" % self.id, 'PUT', {"bri": remap})
        self._intensity = value

    @property
    def transitiontime(self):
        """
        Gets the lights transitiontime
        """
        return self._transitiontime

    @transitiontime.setter
    def transitiontime(self, value):
        """
        Sets the lights transitiontime from one state to another
        Value: integer in milliseconds
        Example: 10 = 1 second
        """
        self.bridge.request("lights/%s/state" % self.id, 'PUT', {"transitiontime": value * 10})
        self._transitiontime = value

    @property
    def loop(self):
        """
        Returns True if the light is in a color loop or False if not
        """
        return self._loop


    @loop.setter
    def loop(self, value):
        """
        Puts the light in a color loop
        Value: True / False
        """
        if isinstance(value, bool):
            if value:
                self.bridge.request("lights/%s/state" % self.id, 'PUT', {"effect": "colorloop"})
            else:
                self.bridge.request("lights/%s/state" % self.id, 'PUT', {"effect": "none"})
            self._loop = value
        else:
            print "Invalid argument passed"


    def alert(self):
        """
        Blinks the light in its current color
        """
        self.bridge.request("lights/%s/state" % self.id, 'PUT', {"alert": "select"})


class Schedule(object):
    """
    This is a schedule, when created pass it the name as a string and the time as 2nd argument,
    like this date='2007-03-04'time='21:08:12'
    If the date is in the past, an error will be returned, to make sure you have the correct timezone, you can display the bridge's time setting like this:
    bridge.getconfig()["localtime]
    """
    id = None
    _command = None
    description = "created with Python API"

    def __init__(self, name, date, time):
        self.name = name
        self.time = str("%sT%s" % (date, time))

    def __repr__(self):
        return "Schedule: NAME: %s TIME: %s COMMAND: %s" % (self.name, self.time, self.command)

    def toJson(self):
        return {
            "name": self.name,
            "description": self.description,
            "command": self.command,
            "time": self.time
        }

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value


class Schedules(list):
    """
    This list holds all the schedules on the bridge
    """

    def __init__(self, bridge):
        self.bridge = bridge
        super(self.__class__, self).__init__()

    def add(self, item):
        return self.bridge.request("schedules", "POST", item.toJson())
        super(self.__class__, self).append(item)


# mybridge = Bridge()
# mybridge.findbridge()
# mybridge.user = "newdeveloper"
# mybridge.getlights()
#
# # With this function we receive all the schedules from the bridge
# mybridge.getschedules()

# Now we can cycle through all schedules like this
# for each in mybridge.schedules:
#     print each

# # Before adding a schedule, we have to initiate schedules
# myschedules = mybridge.getschedules()
#
# # Now we create a new schedule, arguments are name, date and time
# newschedule = Schedule("Wake up", "2014-07-22", "10:40:30")
#
#
# # The command looks something like this, in that case it will turn on the light nr. 1, at the moment you have to provide it with a raw dict, but this might be easier in the future
# newschedule.command = dict(address=("%s/api/%s/lights/3/state/" % (mybridge.adress, mybridge.user)).encode("ascii"),
#                             method="PUT", body={"on": "true"})
#
# # To add the new schedule to the bridge all we have to do is to add it to this list, rest is taken care of
# mybridge.schedules.add(newschedule)
#
# # Show the bridges schedules and you see its now added
# myschedules = mybridge.getschedules()
# print myschedules

print "TEST123"