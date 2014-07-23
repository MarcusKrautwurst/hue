import hue_api as hue
reload(hue)


mybridge = hue.Bridge()
mybridge.findbridge()
mybridge.user = "newdeveloper"

# With this function we receive all lights from the bridge
mybridge.getlights()

# With this function we receive all the schedules from the bridge
myschedules = mybridge.getschedules()
print myschedules



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
