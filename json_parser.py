import json

mode = "auto"
PictureInterval = 1
LogInterval = 300
BTScanInterval = 5
MessageBackend = "Discord"

# MessageBackend cannot be changed without a restart

# the config state is read into config, which is temporary. Then, it is moved into the variables here.

# state from config file
config = {
    "MessageBackend": "discord",
    "PictureInterval": 1,
    "LogInterval": 300,
    "Mode": "auto",
    "BTScanInterval": 5,
}

def init_config():
    global mode
    global PictureInterval
    global LogInterval
    global BTScanInterval
    global MessageBackend
    temp = open("config/config.json")
    dat = json.load(temp)
    for i in dat.keys():
        if i in config.keys():
            config[i] = dat[i];
    mode = config["Mode"]
    PictureInterval = config["PictureInterval"]
    LogInterval = config["LogInterval"]
    BTScanInterval = config["BTScanInterval"]
    MessageBackend = config["MessageBackend"]