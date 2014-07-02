hue
===

Phillips Hue Python API
HOW TO USE 


Create an instance of your bridge
mybridge = Bridge()

Attempt to find your bridge
mybridge.findbridge()

If no bridge is found, we can alternatively do this
#mybridge.set_manual("192.168.0.50")

If we already have a user on the bridge, we set it like this
mybridge.user = "newdeveloper"

If we dont have a user setup, we can create on like this, it will automatically use it after creation
mybridge.createuser("newdeveloper")

Gather all lights from your bridge
mybridge.findlights()

Now we can cycle through them all like this
for light in mybridge.lights:
    Turns this light on
    light.intensity = 0.0
    light.IsOn = True

    Slowly dim this light on
    for i in range(0,10):
        light.intensity += 0.1
        time.sleep(0.1)

    Change the color of this light to red
    light.color = (255,0,0)

    You can also set them with predefined lights
    light.color = light.colors["green"]

    To get a list of predefined colors do this
    #print light.colors

    Plays an alert on this light
    light.alert()

    Cycles through all the colors
    light.loop = True
