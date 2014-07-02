__author__ = "marcus.krautwurst"
__version__ = 0.1

import json
import urllib2
import urllib
import time
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

    def __init__(self,adress=None):
        pass

    def createuser(self, user, description="python_api"):
        userexist = None
        success = False

        check = json.load(urllib2.urlopen('%s/api/%s'%(self.adress,user)))
        try:
            check[0]["error"]["type"]==1
        except KeyError:
            userexist = True

        # If the user doesnt exist, we create him here
        if userexist:
            dataToJson = json.dumps({"devicetype":description,"username":user})
            opener = urllib2.build_opener(urllib2.HTTPHandler)
            request = urllib2.Request('%s/api'%self.adress, data=dataToJson)
            response = opener.open(request)
            response = json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))
            try:
                response[0]["error"]["type"]==101
                print 'To create this user, press the link button and run this function again within 30 seconds'

            except KeyError:
                try:
                    response[0]["success"]
                    self.user = user
                    success = True
                    print "User: '%s' successfully created"%user
                except KeyError:
                    print 'There was an error creating this user'
                    success = False

        return success

    def findbridge(self):
        """
        Attempts to find a bridge on your local network
        """
        find = json.load(urllib2.urlopen('http://www.meethue.com/api/nupnp'))
        if len(find)>0:
            try:
                self.ip = find[0]["internalipaddress"]
                self.adress = "http://%s"%self.ip
                print 'Found bridge at %s'%find[0]["internalipaddress"]
                return True

            except KeyError:
                print "No bridge found"
                return False
        else:
            print "No bridge found"
            return False

    def set_manual(self,ip):
        self.ip = ip
        self.adress = "http://%s"%ip


    def findlights(self):
        """
        Receive all the lights
        """
        if self.user != None:
            readLights= json.load(urllib2.urlopen('%s/api/%s/lights'%(self.adress,self.user)))
            for light in readLights:
                # Here we create the light instance
                mylight = Light(self)
                mylight.name = readLights[light]["name"]
                mylight.id = light
                self.lights.append(mylight)

            return True
        else:
            print "No valid user, please create one or use an existing one"
            return False

    def request(self,url,data,method):
        """
        Sends a request to the bridge
        url: the url that's being added to the base url
        data: usually a dictionary
        method: GET, POST, PUT
        """
        if self.user != None:
            RequestisValid = False

            for each in [url,method]:
                if isinstance(each,str):
                    RequestisValid = True


            if RequestisValid:
                dataToJson = json.dumps(data)
                opener = urllib2.build_opener(urllib2.HTTPHandler)

                if method.upper()=='PUT':
                    request = urllib2.Request('%s/api/%s/%s'%(self.adress,self.user,url), data=dataToJson)
                    request.add_header('Content-Type', 'your/contenttype')
                    request.get_method = lambda: method.upper()
                    response = opener.open(request)
                    return response.read()

                elif method.upper()=='POST':
                    request = urllib2.Request('%s/api/%s/%s'%(self.adress,self.user,url), data=urllib.urlencode(dataToJson))
                    request.add_header('Content-Type', 'your/contenttype')
                    request.get_method = lambda: method.upper()
                    response = opener.open(request)
                    return json.loads(response.read().decode(response.info().getparam('charset') or 'utf-8'))

                elif method.upper()=='GET':
                    return json.load(urllib2.urlopen('%s/api/%s/%s'%(self.adress,self.user,url)))
            else: Exception("False request data")
        else:
            print "Couldn't make a request: No valid user"
            return False

class Group(object):
    """
    This is a group of lights
    """
    name = None
    lights = []

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
    _IsOn = None
    _transitiontime = 10
    _loop = False


    # Public properties
    bridge = None
    id = 0

    # Color presets
    colors={
        "red":(255,0,0),
        "green":(0,255,0),
        "blue":(0,0,255),
        "yellow":(255,255,0),
        "turquoise":(0,255,255)
    }

    def __init__(self,bridge):
        self.bridge = bridge
        pass

    def __repr__(self):
        return "Light: ID: %s NAME: %s"%(self.id,self._name)


    def _RGBToXY(self,r,g,b):
        """
        Private method
        Converts rgb color into xy values for setting the color
        This function is extracted from Tim Rijckaert
        http://stackoverflow.com/questions/22564187/rgb-to-philips-hue-hsb
        """

        normcol = [r/255,g/255, b/255]

        if normcol[0] > 0.04045:
            red = math.pow((normcol[0]+0.055 / (1.0 + 0.055)),2.4)
        else:
            red = normcol[0] / 12.92

        if normcol[1] > 0.04045:
            green = math.pow((normcol[1]+0.055 / (1.0 + 0.055)),2.4)
        else:
            green = normcol[1] / 12.92

        if normcol[2] > 0.04045:
            blue = math.pow((normcol[2]+0.055 / (1.0 + 0.055)),2.4)
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
    def name(self,value):
        """
        Sets the lights name
        """
        value = str(value)
        if isinstance(value,str):
            #TODO Setting the name on a light doesnt work
            request = self.bridge.request("lights/%s/state"%self.id , {"name":value} , 'PUT')
            self._name = value

    @property
    def IsOn(self):
        """
        Returns if the light is on or not
        """
        return self._IsOn

    @IsOn.setter
    def IsOn(self,value):
        """
        Turns the light on or off
        Type: bool
        """
        self.bridge.request("lights/%s/state"%self.id , {"on":value} , 'PUT')
        self._IsOn = value



    @property
    def color(self):
        """
        Gets the lights color
        """
        return self._color

    @color.setter
    def color(self,col):
        """
        Sets the lights color
        Example: (255,0,0) for red
        Alternatively you can also use the local dict colors with presets
        Example: self.colors["red"]
        """
        color = self._RGBToXY(col[0],col[1],col[2])
        self.bridge.request("lights/%s/state"%self.id , {"xy":color} , 'PUT')

        self._color = col
        pass

    @property
    def saturation(self):
        """
        Gets the lights saturation
        """
        return self._saturation

    @saturation.setter
    def saturation(self,value):
        """
        Sets the lights saturation
        Range: 0-255
        """
        self.bridge.request("lights/%s/state"%self.id , {"sat":value} , 'PUT')
        self._saturation = value

    @property
    def intensity(self):
        """
        Gets the lights intensity
        """
        return self._intensity

    @intensity.setter
    def intensity(self,value):
        """
        Sets the lights intensity
        Range: 0.0 <=> 1.0
        """
        if value<0.001:
            value=0.001
        elif value>1.0:
            value=1.0

        #Remaps value internally from 0-1 to 0-255 (the range the bridge accepts)
        #TODO: Test this more, can it fail?
        remap = int(round((value / 1.0) * 255,0))

        self.bridge.request("lights/%s/state"%self.id , {"bri":remap} , 'PUT')
        self._intensity = value

    @property
    def transitiontime(self):
        """
        Gets the lights transitiontime
        """
        return self._transitiontime

    @transitiontime.setter
    def transitiontime(self,value):
        """
        Sets the lights transitiontime from one state to another
        Value: integer in milliseconds
        Example: 10 = 1 second
        """
        self.bridge.request("lights/%s/state"%self.id , {"transitiontime":value*10} , 'PUT')
        self._transitiontime = value

    @property
    def loop(self):
        """
        Returns True if the light is in a color loop or False if not
        """
        return self._loop


    @loop.setter
    def loop(self,value):
        """
        Puts the light in a color loop
        Value: True / False
        """
        if isinstance(value,bool):
            if value:
                self.bridge.request("lights/%s/state"%self.id , {"effect":"colorloop"} , 'PUT')
            else:
                self.bridge.request("lights/%s/state"%self.id , {"effect":"none"} , 'PUT')
            self._loop = value
        else:
            print "Invalid argument passed"


    def alert(self):
        """
        Blinks the light in its current color
        """
        self.bridge.request("lights/%s/state"%self.id , {"alert":"select"} , 'PUT')



# Create an instance of your bridge
mybridge = Bridge()

# Attempt to find your bridge
mybridge.findbridge()

# If no bridge is found, we can alternatively do this
#mybridge.set_manual("192.168.0.50")

# If we already have a user on the bridge, we set it like this
mybridge.user = "newdeveloper"

# If we dont have a user setup, we can create on like this, it will automatically use it after creation
#mybridge.createuser("newdeveloper")

# Gather all lights from your bridge
mybridge.findlights()

# Now we can cycle through them all like this
for light in mybridge.lights:
    # Turns this light on
    light.intensity = 0.0
    light.IsOn = True

    # Slowly dim this light on
    for i in range(0,10):
        light.intensity += 0.1
        time.sleep(0.1)

    # Change the color of this light to red
    light.color = (255,0,0)

    # You can also set them with predefined lights
    light.color = light.colors["green"]

    # To get a list of predefined colors do this
    #print light.colors

    # Plays an alert on this light
    light.alert()

    # Cycles through all the colors
    light.loop = True
