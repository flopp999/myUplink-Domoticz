# myUplink Python Plugin
#
# Author: flopp999
#
"""
<plugin key="myUplink" name="myUplink 0.12" author="flopp999" version="0.12" wikilink="https://github.com/flopp999/myUplink-Domoticz" externallink="https://www.myuplink.com">
    <description>
        <h2>myUplink is used to read data from api.myuplink.com</h2><br/>
        <h2>Support me with a coffee &<a href="https://www.buymeacoffee.com/flopp999">https://www.buymeacoffee.com/flopp999</a></h2><br/>
        <h1>To use this plugin you need to agree to send data to me. I will use the data to develop the plugin so it will fit all NIBE systems</h1>
        <h3>You can see what data I have collect by follow this link. I will onlt collect data once after startup. It will include all your parameters, your SystemID and you categories.</h3>
        <h3>&<a href="https://rhematic-visitors.000webhostapp.com/[your systemid]">https://rhematic-visitors.000webhostapp.com/[your systemid]</a></h3>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>..</li>
        </ul>
        <h3>How to get your Identifier, Secret and URL?</h3>
        <h4>&<a href="https://github.com/flopp999/myUplink-Domoticz#identifier-secret-and-callback-url">https://github.com/flopp999/myUplink-Domoticz#identifier-secret-and-callback-url</a></h4>
        <h3>How to get your Access Code?</h3>
        <h4>&<a href="https://github.com/flopp999/myUplink-Domoticz#access-code">https://github.com/flopp999/myUplink-Domoticz#access-code</a></h4>
        <h3>Configuration</h3>
    </description>
    <params>
        <param field="Mode5" label="Agree to send data to developer of this plugin" width="70px" required="true">
            <options>
                <option label="Yes" value=True />
                <option label="No" value=False />
            </options>
        </param>
        <param field="Mode4" label="myUplink Identifier" width="320px" required="true" default="Identifier"/>
        <param field="Mode2" label="myUplink Secret" width="350px" required="true" default="Secret"/>
        <param field="Address" label="myUplink Callback URL" width="950px" required="true" default="URL"/>
        <param field="Mode6" label="Debug to file (myUplink.log)" width="70px">
            <options>
                <option label="Yes" value="Yes" />
                <option label="No" value="No" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz

Package = True

try:
    import requests, json, os, logging
except ImportError as e:
    Package = False

try:
    from logging.handlers import RotatingFileHandler
except ImportError as e:
    Package = False

try:
    from datetime import datetime
except ImportError as e:
    Package = False

dir = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("myUplink")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(dir+'/myUplink.log', maxBytes=1000000, backupCount=5)
logger.addHandler(handler)

categories = ["AUX_IN_OUT", "STATUS", "CPR_INFO_EP14", "VENTILATION", "SYSTEM_1", "ADDITION", "SMART_PRICE_ADAPTION", "SYSTEM_INFO", "SYSTEM_2", "HEAT_METER", "ACTIVE_COOLING_2_PIPE", "PASSIVE_COOLING_INTERNAL", "PASSIVE_COOLING_2_PIPE", "DEFROSTING", "SMART_ENERGY_SOURCE_PRICES", "EME", "HTS1"]

class BasePlugin:
    enabled = False

    def __init__(self):
        self.token = ''
        self.loop = 0
        self.Count = 5
        return

    def onStart(self):
#        Domoticz.Debugging(1)
        WriteDebug("===onStart===")
        self.Ident = Parameters["Mode4"]
        self.URL = Parameters["Address"]
        self.Access = Parameters["Mode1"]
        self.Secret = Parameters["Mode2"]
        self.Refresh = Parameters["Mode3"]
        self.SystemID = ""
        self.NoOfSystems = ""
        self.SystemUnitId = 0
        self.FirstRun = True
        self.Agree = Parameters["Mode5"]
        self.AllSettings = True
        self.Categories = []
        self.Connections = {}

        if len(self.Ident) < 36:
            Domoticz.Log("Identifier too short")
            WriteDebug("Identifier too short")

        if len(self.URL) < 10:
            Domoticz.Log("URL too short")
            WriteDebug("URL too short")

#        if len(self.Access) < 370:
#            Domoticz.Log("Access Code too short")
#            WriteDebug("Access Code too short")

        if len(self.Secret) < 32:
            Domoticz.Log("Secret too short")
            WriteDebug("Secret too short")
        else:
            self.Secret = self.Secret.replace("+", "%2B")

#        if len(self.Refresh) < 270:
#            Domoticz.Log("Refresh too short")
#            WriteDebug("Refresh too short")

        if self.Agree == "null":
            Domoticz.Log("You need to agree")
            WriteDebug("Not agree")
            self.Agree == "False"
        if os.path.isfile(dir+'/myUplink.zip'):
            if 'myUplink' not in Images:
                Domoticz.Image('myUplink.zip').Create()
            self.ImageID = Images["myUplink"].ID




        if self.Agree == "True":
            self.GetRefresh = Domoticz.Connection(Name="Get Refresh", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
            if len(self.Refresh) < 50 and self.AllSettings == True:
                self.GetRefresh.Connect()
            self.GetToken = Domoticz.Connection(Name="Get Token", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
            self.GetData = Domoticz.Connection(Name="Get Data 0", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
            self.GetCategories = Domoticz.Connection(Name="Get Categories", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
            self.GetSystemID = Domoticz.Connection(Name="Get SystemID", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
            self.GetNoOfSystems = Domoticz.Connection(Name="Get NoOfSystems", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")
            self.GetTarget = Domoticz.Connection(Name="Get Target", Transport="TCP/IP", Protocol="HTTPS", Address="api.myuplink.com", Port="443")

    def onDisconnect(self, Connection):
        WriteDebug("onDisconnect called for connection '"+Connection.Name+"'.")

    def onConnect(self, Connection, Status, Description):
        WriteDebug("onConnect")
        if CheckInternet() == True and self.AllSettings == True:
            if (Status == 0):
                headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Host': 'api.myuplink.com'}
                data = "client_id="+self.Ident
                data += "&client_secret="+self.Secret

                if Connection.Name == ("Get Token"):
                    WriteDebug("Get Token")
                    data += "&grant_type=client_credentials"
                    Connection.Send({'Verb':'POST', 'URL': '/oauth/token', 'Headers': headers, 'Data': data})

                headers = { 'Host': 'api.myuplink.com', 'Authorization': 'Bearer '+self.token}

                if Connection.Name == ("Get Data 0"):
                    WriteDebug("Get Data 0")
                    Connection.Send({'Verb':'GET', 'URL': '/v2/devices/'+self.SystemID+'/points', 'Headers': headers})
                    Domoticz.Log("Data updated")

                elif Connection.Name == ("Get Categories"):
                        WriteDebug("Get Categories")
                        self.SystemUnitId = 0
                        while self.SystemUnitId < int(self.NoOfSystems):
                            Connection.Send({'Verb':'GET', 'URL': '/api/v1/systems/'+self.SystemID+'/serviceinfo/categories?systemUnitId='+str(self.SystemUnitId), 'Headers': headers})
                            self.SystemUnitId += 1

                elif Connection.Name == ("Get SystemID"):
                        WriteDebug("Get SystemID")
                        Connection.Send({'Verb':'GET', 'URL': '/v2/systems/me', 'Headers': headers})

    def onMessage(self, Connection, Data):
        Status = int(Data["Status"])

        if (Status == 200) and self.Agree == "True":
            Data = Data['Data'].decode('UTF-8')
            Data = json.loads(Data)

            if Connection.Name == ("Get Categories"):
                for each in Data:
                    self.Categories.append(each["categoryId"])
                requests.post(url='https://rhematic-visitors.000webhostapp.com/a.php?file='+str(self.SystemID)+'&data='+str(self.Categories), timeout=2)
                self.Categories = []
                self.GetCategories.Disconnect()
                self.GetData.Connect()

            elif Connection.Name == ("Get SystemID"):
                self.SystemID = str(Data["systems"][0]["devices"][0]["id"])
                self.GetSystemID.Disconnect()
                self.GetData.Connect()

            elif Connection.Name == ("Get Token"):
                self.token = Data["access_token"]
                self.GetToken.Disconnect()
                if self.SystemID == "":
                    self.GetSystemID.Connect()
                else:
                    self.GetData.Connect()

            elif Connection.Name == ("Get Data 0"):
                for each in Data:
                    sValue = each["value"]
                    UpdateDevice(str(sValue), each["parameterUnit"], each["parameterName"], int(each["parameterId"]), self.SystemID)


        elif self.Agree == "False":
            Domoticz.Log("You must agree")
        else:
            WriteDebug("Status = "+str(Status))
            Domoticz.Error(str("Status "+str(Status)))
            Domoticz.Error(str(Data))
            if _plugin.GetRefresh.Connected():
                _plugin.GetRefresh.Disconnect()
            if _plugin.GetToken.Connected():
                _plugin.GetToken.Disconnect()
            if _plugin.GetData.Connected():
                _plugin.GetData.Disconnect()
            if _plugin.GetSystemID.Connected():
                _plugin.GetSystemID.Disconnect()
            if _plugin.GetCategories.Connected():
                _plugin.GetCategories.Disconnect()
            if _plugin.GetTarget.Connected():
                _plugin.GetTarget.Disconnect()
            if _plugin.GetNoOfSystems.Connected():
                _plugin.GetNoOfSystems.Disconnect()


    def onHeartbeat(self):
        if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
            _plugin.GetData.Disconnect()
        if _plugin.GetCategories.Connected() or _plugin.GetCategories.Connecting():
            _plugin.GetCategories.Disconnect()
        if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
            _plugin.GetSystemID.Disconnect()
        if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
            _plugin.GetNoOfSystems.Disconnect()
        if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
            _plugin.GetTarget.Disconnect()

        if self.Agree == "True":
            self.Count += 1
            if self.Count == 6 and not self.GetToken.Connected() and not self.GetToken.Connecting():
                self.GetToken.Connect()
                WriteDebug("onHeartbeat")
                self.Count = 0
        else:
            Domoticz.Log("Please agree")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def UpdateDevice(sValue, Unit, Name, PID, SystemUnitId):
    Design="a"
    if PID == 4:
        ID = 1
    elif PID == 12:
        ID = 2
    elif PID == 54:
        ID = 3
    elif PID == 57:
        ID = 4
    elif PID == 64:
        ID = 5
    elif PID == 65:
        ID = 6
    elif PID == 66:
        ID = 7
    elif PID == 91:
        ID = 8
    elif PID == 121:
        ID = 9
    elif PID == 781:
        ID = 10
    elif PID == 994:
        ID = 11
    elif PID == 997:
        ID = 12
    elif PID == 1708:
        ID = 13
    elif PID == 2491:
        ID = 14
    elif PID == 2494:
        ID = 15
    elif PID == 2495:
        ID = 16
    elif PID == 2496:
        ID = 18
    elif PID == 2497:
        ID = 18
    elif PID == 2766:
        ID = 19
    elif PID == 2767:
        ID = 20
    elif PID == 3095:
        ID = 21
    elif PID == 3096:
        ID = 22
    elif PID == 3671:
        ID = 23
    elif PID == 7086:
        ID = 24
    elif PID == 10897:
        ID = 25
    elif PID == 12421:
        ID = 26
    elif PID == 14952:
        ID = 27
    elif PID == 15069:
        ID = 28
    elif PID == 50660:
        ID = 29
    elif PID == 50661:
        ID = 30
    elif PID == 50662:
        ID = 31
    elif PID == 50663:
        ID = 32
    elif PID == 50664:
        ID = 33
    elif PID == 50665:
        ID = 34
    elif PID == 50666:
        ID = 35
    elif PID == 50826:
        ID = 36
    elif PID == 50827:
        ID = 37
    elif PID == 55000:
        ID = 38
    elif PID == 55087:
        ID = 39
    else:
        Domoticz.Error(str(PID))
        if _plugin.FirstRun == True:
            requests.post(url='https://rhematic-visitors.000webhostapp.com/a.php?file=myUplink_'+str(_plugin.SystemID)+'&data='+str(PID)+';'+str(sValue)+';'+str(Unit)+';'+str(Name), timeout=2)
    if (ID in Devices):
        if Devices[ID].sValue != sValue:
            Devices[ID].Update(0, str(sValue))

    if (ID not in Devices):
        if sValue == "-32768":
            Used = 0
        else:
            Used = 1
        if Unit == "bar":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Pressure", Used=1, Description="ParameterID="+str(PID)).Create()
        if Unit == "l/m":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Waterflow", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
        elif Unit == "°C" or ID == 30 and ID !=24:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Temperature", Used=Used, Description="ParameterID="+str(PID)).Create()
        elif Unit == "A":
            if ID == 15:
                Domoticz.Device(Name=Name+" 1", Unit=ID, TypeName="Custom", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 16:
                Domoticz.Device(Name=Name+" 2", Unit=ID, TypeName="Custom", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 17:
                Domoticz.Device(Name=Name+" 3", Unit=ID, TypeName="Custom", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)+"\nSystem="+str(SystemUnitId)).Create()
            if ID == 53:
                Domoticz.Device(Name=Name, Unit=ID, TypeName="Current (Single)", Used=1, Description="ParameterID="+str(PID)+"\nSystem="+str(SystemUnitId)).Create()
        elif Name == "compressor starts":
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;times"}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif Name == "blocked":
            if ID == 21:
                Domoticz.Device(Name="compressor "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
            if ID == 51:
                Domoticz.Device(Name="addition "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 24:
            Domoticz.Device(Name="compressor "+Name, Unit=ID, TypeName="Temperature", Used=1, Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif ID == 41 or ID == 81:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)+"\nDesignation="+str(Design)).Create()
        elif ID == 61:
            Domoticz.Device(Name="comfort mode "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 62:
            Domoticz.Device(Name="comfort mode "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 63:
            Domoticz.Device(Name="smart price adaption "+Name, Unit=ID, TypeName="Custom", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 71:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()
        elif ID == 72 or ID == 73:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID)).Create()
        elif ID == 74:
            Domoticz.Device(Name="software "+Name, Unit=ID, TypeName="Text", Used=1, Image=(_plugin.ImageID)).Create()
        else:
            Domoticz.Device(Name=Name, Unit=ID, TypeName="Custom", Options={"Custom": "0;"+Unit}, Used=1, Image=(_plugin.ImageID), Description="ParameterID="+str(PID)).Create()


def CheckInternet():
    WriteDebug("Entered CheckInternet")
    try:
        WriteDebug("Ping")
        requests.get(url='https://api.myuplink.com/', timeout=2)
        WriteDebug("Internet is OK")
        return True
    except:
        if _plugin.GetRefresh.Connected() or _plugin.GetRefresh.Connecting():
            _plugin.GetRefresh.Disconnect()
        if _plugin.GetToken.Connected() or _plugin.GetToken.Connecting():
            _plugin.GetToken.Disconnect()
        if _plugin.GetData.Connected() or _plugin.GetData.Connecting():
            _plugin.GetData.Disconnect()
        if _plugin.GetData1.Connected() or _plugin.GetData1.Connecting():
            _plugin.GetData1.Disconnect()
        if _plugin.GetCategories.Connected() or _plugin.GetCategories.Connecting():
            _plugin.GetCategories.Disconnect()
        if _plugin.GetSystemID.Connected() or _plugin.GetSystemID.Connecting():
            _plugin.GetSystemID.Disconnect()
        if _plugin.GetNoOfSystems.Connected() or _plugin.GetNoOfSystems.Connecting():
            _plugin.GetNoOfSystems.Disconnect()
        if _plugin.GetTarget.Connected() or _plugin.GetTarget.Connecting():
            _plugin.GetTarget.Disconnect()

        WriteDebug("Internet is not available")
        return False

def WriteDebug(text):
    if Parameters["Mode6"] == "Yes":
        timenow = (datetime.now())
        logger.info(str(timenow)+" "+text)

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    _plugin.onMessage(Connection, Data)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
