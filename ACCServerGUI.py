##WIP James Megenis
# coding=utf-8
import tkinter as tk
from tkinter import ttk
#Loading and saving
import json
#Running the accServer.exe from within the application
import subprocess
#File moving / creation
import os
#list of all the tracks in the game currently. //TODO find a way to pull these from game files
tracklist = ['monza','zolder','brands_hatch','silverstone','paul_ricard','misano','spa','nurburgring','barcelona',
    'zandvoort','monza_2019','zolder_2019','brands_hatch_2019','silverstone_2019','paul_ricard_2019','misano_2019','spa_2019'
    ,'nurburgring_2019','barcelona_2019','zandvoort_2019','kyalami_2019','mount_panorama_2019','suzuka_2019','laguna_seca_2019']
#All allowed fields in settings.json with preset values (NOT COMPLETE)
settings_fields = {
 "serverName": "please enter a server name",
 "adminPassword": " adminPw123",
 "trackMedalsRequirement": [0,3],
 "safetyRatingRequirement": [0,100],
 "racecraftRatingRequirement": [-1,100],
 "password": "",
"spectatorPassword": "",
 "maxCarSlots": 30,
 "dumpLeaderboards": ['No','Yes'],
 "isRaceLocked": ['Yes', 'No'],
 "randomizeTrackWhenEmpty": ['Yes', 'No'],
 "centralEntryListPath": "",
 "allowAutoDQ": ['Yes', 'No'],
 "shortFormationLap": ['Yes', 'No'],
 "dumpEntryList": ['No','Yes'],
 "formationLapType": ['Default', 'Old Limiter Lap','Free']
}
#All allowed fields in event.json with preset values. Sessions to be added later (NOT COMPLETE)
event_fields = {
    "track": tracklist,
    "preRaceWaitingTimeSeconds": 60,
    "sessionOverTimeSeconds": 120,
    "ambientTemp": 26,
    "cloudLevel": 0.3,
    "rain": 0.0,
    "weatherRandomness": [0,1,2,3,4,5,6,7],
    "configVersion": 1,
    } #sessions : [{},{},{}]
#Sessions is a list of session_fields dictionaries. To be appended to event_fields before saving and removed after loading.
sessions =[
    {
    "sessionType": ['practice','qualifying','race'],
    "hourOfDay": 10,
    "dayOfWeekend": ['Friday','Saturday','Sunday'],
    "timeMultiplier": [0,24],
    "sessionDurationMinutes": 20
    },
    {
    "sessionType": ['qualifying','practice','race'],
    "hourOfDay": 13,
    "dayOfWeekend":['Saturday','Friday','Sunday'],
    "timeMultiplier": [0,24],
    "sessionDurationMinutes": 10
    },
    {
    "sessionType": ['race','practice','qualifying'],
    "hourOfDay": 13,
    "dayOfWeekend":['Sunday','Friday','Saturday'],
    "timeMultiplier":[0,24],
    "sessionDurationMinutes": 20
    }
    ]
#All values for each session
session_fields = {'sessionType':['practice','qualifying','race'],'hourOfDay':10,'dayOfWeekend':[1,2,3],'timeMultiplier':[0,24],'sessionDurationMinutes':10}
##All allowed fields in assistRules.json with preset values (NOT COMPLETE)
assist_fields = {
	"disableIdealLine": ['Yes', 'No'],
	"disableAutosteer": ['Yes', 'No'],
    "stabilityControlLevelMax": [0,100],
	"disableAutoPitLimiter": ['Yes', 'No'],
    "disableAutoGear": ['Yes', 'No'],
	"disableAutoClutch": ['Yes', 'No'],
	"disableAutoEngineStart": ['Yes', 'No'],
	"disableAutoWiper": ['Yes', 'No'],
	"disableAutoLights": ['Yes', 'No']
}
##All allowed fields in eventRules.json with preset values (NOT COMPLETE)
event_rules_fields = {
 "qualifyStandingType": ['Fastest Lap','Average lap(Not officially supported)'],
 "pitWindowLengthSec": -1,
 "driverStintTimeSec": -1,
 "mandatoryPitstopCount": 0,
 "maxTotalDrivingTime": -1,
 "maxDriversCount": [0,1,3,4,5], #can be changed to add more drivers
 "isRefuellingAllowedInRace": ['Yes ', 'No '],
 "isRefuellingTimeFixed": ['Yes ', 'No '],
 "isMandatoryPitstopRefuellingRequired": ['Yes ', 'No '],
 "isMandatoryPitstopTyreChangeRequired": ['Yes ', 'No '],
 "isMandatoryPitstopSwapDriverRequired":['Yes ', 'No ']
 }
##All allowed fields in configuration.json with preset values (NOT COMPLETE)
configuration_fields = {
 "udpPort": 9321,
 "tcpPort": 9321,
 "maxConnections": 85,
 "lanDiscovery": 1,
 "registerToLobby": 1,
 "configVersion": 1
}

##Creates a form from a dictionary. With a label on the left side and some kind of input widget on the right
#[0,0] integer lists will be made into sliding scales
#['item1','item2'] string lists will be made into drop downs
#"string1" strings will be Entry boxes. Goal is to use as few of these as possible to prevent user error
def makeform(root, fields):
    entries = {}
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=31, text=field+": ", anchor='w')
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        lab.pack(side=tk.LEFT)
        #for lists will create a drop down mennu in the form. Used for categories with a relatively small amount of options
        if isinstance(fields[field], list):
            if isinstance(fields[field][0],int) :
                ent = tk.Scale(row, from_=fields[field][0], to=fields[field][-1], orient=tk.HORIZONTAL)
                ent.pack()
            else:
                ent = tk.StringVar(root)#the entry is the string value taken.
                ent.set(fields[field][0]) # default value
                a = tk.OptionMenu(row, ent, *fields[field])
                a.pack()

        #for string or integer variables will take as text input
        else:
            ent = tk.Entry(row)
            ent.insert(0, fields[field])
            ent.pack(side=tk.RIGHT,
                     expand=tk.YES,
                     fill=tk.X,
                     ipadx= 10)

        entries[field] = ent
    return entries

#Saves into the program the values currently entered by the user(These are not retained on program close).
#Useful if something needs to be done with a current input value. But not saving the files to a json. E.g adding a new session
def getValues():
    ##Saves values in the system
    for i in settings_fields:
        settings_fields[i] = show_settings[i].get()
    #print(show_settings[i].get())

    for i in assist_fields:
        assist_fields[i] = show_assists[i].get()
        #print(show_assists[i].get())
    #print(event_fields)
    for i in event_fields:
        #print(i)
        event_fields[i] = show_event[i].get()
        #print(show_event[i].get())

    #for each session:
    for i in range(len(sessions)):
        for x in session_fields:
            sessions[i][x] = show_sessions[i][x].get()

    #print(session_fields)
    for i in event_rules_fields:
        event_rules_fields[i] = show_event_rules[i].get()
        #print(show_event_rules[i].get())

    for i in configuration_fields:
        configuration_fields[i] = show_config[i].get()
    #    print(show_config[i].get())

    #Could return all values found in some way. However given values are mostly global. Not nescesary
    return
    ##Form to take inputs from the program.
    ##Add validation for type(string,int,double)

#Writes current selection into jsons that the accServer.exe can understand
def WriteJson():

    getValues()
    #Adds the updated sessions into the event fields
    event_fields_full = {k: v for k, v in event_fields.items()}
    event_fields_full['sessions'] = sessions
    conversion = {"Yes":1,"No":0,"Yes ": "true","No ":"false","Default":"3","Old Limiter Lap":"0","Free":"1","Fastest Lap":"1","Average lap(Not officially supported)":"2"}
    #Conversion to readable data for the server
    for x in [settings_fields,configuration_fields,assist_fields,event_fields_full,event_rules_fields]:
        for i in x:
            for y in conversion:
                if x[i] == (y):
                    x[i] = conversion[y]


    #Creation of file location if one doesnt already exist
    path =os.getcwd()+"/cfg/"
    print(path)
    try:
        os.makedirs(path)
    except OSError:
        print ("Creation of the directory %s failed. It probably already exists." % path)
    else:

        print ("Directory Created: %s " % path)

    #write dictionaries to json files
    with open(path +'settings.json', 'w') as outfile:
        json.dump(settings_fields, outfile,indent=4)
    with open(path +'configuration.json', 'w') as outfile:
        json.dump(configuration_fields, outfile,indent=4)

    with open(path +'event.json', 'w') as outfile:
        json.dump(event_fields_full, outfile,indent=4)
    with open(path +'eventRules.json','w') as outfile:
        json.dump(event_rules_fields,outfile,indent = 4)
    with open(path +'assistRules.json', 'w') as outfile:
        json.dump(assist_fields, outfile,indent=4)

def RunaccServer():
#    subprocess.run("accServer") currently causes an error
    return

if __name__ == '__main__':
    root = tk.Tk()
    root.title("ACC Server Creator")
    #Creating the tabs
    tab_main=ttk.Notebook(root)

    #print(event_fields_full.keys())
    ##settings
    frame_settings = ttk.Frame(tab_main,relief=tk.RAISED, borderwidth=1)
    frame_settings.pack(fill = tk.Y,side=tk.LEFT)
    show_settings = makeform(frame_settings,settings_fields)


    ##Assists
    frame_assists = ttk.Frame(tab_main,relief=tk.RAISED, borderwidth=1)
    frame_assists.pack(fill = tk.Y,side=tk.LEFT)
    show_assists = makeform(frame_assists,assist_fields)

    ##Config
    frame_config= ttk.Frame(tab_main,relief=tk.RAISED, borderwidth=1)
    frame_config.pack(fill = tk.Y,side=tk.LEFT)
    show_config = makeform(frame_config,configuration_fields) #more effecient use of space

    ##Evennt
    frame_event = tk.Frame(root,relief=tk.RAISED, borderwidth=1)
    frame_event.pack(fill = tk.Y,side=tk.LEFT)
    show_event = makeform(frame_event,event_fields)

    ##Sessions (within event)
    frame_sessions= tk.Frame(root,relief=tk.RAISED, borderwidth=1)
    frame_sessions.pack(fill = tk.Y,side=tk.LEFT)
    #Creates a list of frame_sessions so that each session has its own options
    show_sessions = []
    for i in sessions:
        show_sessions.append(makeform(frame_sessions,i))

    ##rules
    frame_event_rules = tk.Frame(root,relief=tk.RAISED, borderwidth=1)
    frame_event_rules.pack(fill = tk.Y,side=tk.LEFT)
    show_event_rules = makeform(frame_event_rules,event_rules_fields)


    #Save, load, run, submit buttons
    frame_buttons = tk.Frame(root,relief=tk.RAISED, borderwidth=1)
    frame_buttons.pack(side=tk.BOTTOM)
    submit_Button = tk.Button(frame_buttons, text='Save Settings',command = WriteJson) #change name
    run_Button = tk.Button(frame_buttons, text='Run accServer',command = RunaccServer)
    load_Button = tk.Button(frame_buttons, text='Load config')
    save_Button = tk.Button(frame_buttons, text='Save config')
    submit_Button.pack(side=tk.RIGHT)
    run_Button.pack(side=tk.RIGHT)
    load_Button.pack(side=tk.RIGHT)
    save_Button.pack(side=tk.RIGHT)

    #each frame becomes a tab
    tab_main.add(frame_settings, text="settings")
    tab_main.add(frame_assists,text = "assists")
    tab_main.add(frame_event,text = "events")
    tab_main.add(frame_sessions,text = "sessions")
    tab_main.add(frame_event_rules,text = "event rules")
    tab_main.add(frame_config,text = "Network Settings")
    tab_main.pack(expand=1,fill="both")

    root.mainloop()
