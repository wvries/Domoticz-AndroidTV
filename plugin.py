"""
<plugin key="AndroidTV" name="Android TV integration into Domoticz" author="wvries" version="0.0.1">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="40px" required="true" default="5555"/>
        <param field="Mode1" label="MAC Address (WOL)" width="200px" required="false" default=""/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="True" />
            </options>
        </param>
    </params>
</plugin>
"""
#
# Main Import
import Domoticz
import socket
import subprocess
import struct
import re
import configparser
import os
import sys

class BasePlugin:
 # Connection Status
 isConnected = -1
 volume = -1
 initialized = 0

 def __init__(self):
     return

 def onStart(self):
    self.initialized = 0
    if Parameters["Mode6"] == "Debug":
        Domoticz.Debugging(1)
    try:
      dbfilename = os.path.join(os.path.dirname(__file__), 'database.ini' )
      self.cfg = configparser.ConfigParser()
      self.cfg.optionxform = str
      self.cfg.read(dbfilename)
    except Exception as e:
        Domoticz.Log(str(e))
        self.initialized = 0
        return False
    if (len(Devices) == 0):
      try:
        Domoticz.Device(Name="Status",  Unit=1, Type=17, Image=2, Switchtype=17, Used=1).Create()
        ase = 'Sources'
        levelac = ""
        levelnames = "Off"
        st = "0"
        hs = "true"
        if self.cfg.has_section(ase):
         ops = self.cfg.options(ase)
         for o in ops:
          levelac    += "|"
          levelnames += "|"+str(o)
         if len(ops)>4:
          st = "1"
          hs = "false"
        Options =   {   "LevelActions"  : levelac ,
                        "LevelNames"    : levelnames,
                        "LevelOffHidden": hs,
                        "SelectorStyle" : st
        }
        Domoticz.Device(Name="Source",  Unit=2, TypeName="Selector Switch", Switchtype=18, Image=12, Options=Options, Used=1).Create()
        Domoticz.Device(Name="Volume",  Unit=3, Type=244, Subtype=73, Switchtype=7, Image=8, Used=1).Create()
        Domoticz.Device(Name="App",     Unit=4, Type=243, Subtype=19, Used=1).Create()
        ase = 'Apps'
        levelac = ""
        levelnames = "Off"
        st = "0"
        hs = "true"
        if self.cfg.has_section(ase):
         ops = self.cfg.options(ase)
         for o in ops:
          levelac    += "|"
          levelnames += "|"+str(o)
         if len(ops)>4:
          st = "1"
          hs = "false"
        Options =   {   "LevelActions"  : levelac ,
                        "LevelNames"    : levelnames,
                        "LevelOffHidden": hs,
                        "SelectorStyle" : st
        }
        Domoticz.Device(Name="App Selector",  Unit=5, TypeName="Selector Switch", Switchtype=18, Image=12, Options=Options, Used=1).Create()
        ase = 'Remote'
        levelac = ""
        levelnames = "Off"
        st = "0"
        hs = "true"
        if self.cfg.has_section(ase):
         ops = self.cfg.options(ase)
         for o in ops:
          levelac    += "|"
          levelnames += "|"+str(o)
         if len(ops)>4:
          st = "1"
          hs = "false"
        Options =   {   "LevelActions"  : levelac ,
                        "LevelNames"    : levelnames,
                        "LevelOffHidden": hs,
                        "SelectorStyle" : st
        }
        Domoticz.Device(Name="Remote commands",  Unit=6, TypeName="Selector Switch", Switchtype=18, Image=18, Options=Options, Used=1).Create()

        Domoticz.Log("Devices created.")
      except Exception as e:
        Domoticz.Log(str(e))
        self.initialized = 0
        return False

    Domoticz.Heartbeat(10)
    self.config = {
            "host"       :  Parameters["Address"],
            "port"       :  int(Parameters["Port"]),
            "mac"        :  Parameters["Mode1"]
    }
    Domoticz.Log("Connecting to: "+Parameters["Address"]+":"+Parameters["Port"])
    self.isConnected = -1
    self.volume = -1
    self._isAlive()
    if self.isConnected == 1:
      try:
       subprocess.run(["adb", "connect", self.config["host"]+":"+str(self.config["port"])], timeout=5 )
      except:
       pass
    self.initialized = 1
    return True

 def onStop(self):
     Domoticz.Debug("onStop called")
     if self.isConnected == 2:
      try:
       subprocess.run(["adb", "disconnect", self.config["host"]+":"+str(self.config["port"])], timeout=1 )
      except:
       pass

 def _isAlive(self):
    origstat = self.isConnected
    socket.setdefaulttimeout(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((self.config["host"], self.config["port"]))
        if self.isConnected < 1:
         self.isConnected = 1 # port opened
    except socket.error as e:
        self.isConnected = 0
    s.close()
    if self.isConnected > 0:
     try:
      log = str(subprocess.check_output("adb -s "+self.config["host"]+":"+str(self.config["port"])+ " get-state", shell=True, timeout=2))
      if ("device" in log) and ("error" not in log):
       self.isConnected = 2
      else:
       Domoticz.Debug("ADB error "+log)
     except:
      pass
    if self.isConnected != origstat:
     if self.isConnected == 0:
       Domoticz.Heartbeat(20)
     else:
       Domoticz.Heartbeat(10)

    if Parameters["Mode6"] == "Debug":
            Domoticz.Log("isAlive status :" +str(self.isConnected))
    return

 def _wakeonlan(self):
     mac = str(self.config["mac"]).strip().upper()
     if len(mac) > 2:
      try:
           Domoticz.Debug("WOL "+str(mac))
           if ":" in mac:
            addr_byte = mac.split(':')
           elif "-" in mac:
            addr_byte = mac.split('-')
           else:
            addr_byte = []
           if len(addr_byte)>4:
            hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
                                  int(addr_byte[1], 16),
                                  int(addr_byte[2], 16),
                                  int(addr_byte[3], 16),
                                  int(addr_byte[4], 16),
                                  int(addr_byte[5], 16))
            msg = b'\xff' * 6 + hw_addr * 16
            socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            socket_instance.sendto(msg, ('<broadcast>', 9))
            socket_instance.close()
      except Exception as e:
       Domoticz.Debug("WOL error"+str(e))

 def onCommand(self, Unit, Command, Level, Color):  # react to commands arrived from Domoticz
    Command = Command.strip()

    cmdConnect = "adb -s "+Parameters["Address"]+":"+Parameters["Port"]+" "

    if (Unit == 1):  # Status
         if (Command == 'On'):
            if (self.isConnected >= 1):
              try: #adb switch on
               Domoticz.Debug("Switching TV On")
               subprocess.run(["adb", "-s", self.config["host"]+":"+str(self.config["port"]),"shell","input","keyevent","224"], timeout=2 )
              except:
               pass
            else:
             self._wakeonlan() #WOL
         else:
            if (self.isConnected >= 1):
              try: #switch off
               cmd = cmdConnect + "shell input keyevent 223"
               result1 = subprocess.run([cmd], shell=True, capture_output=True, text=True, timeout=2)
              except:
               pass
            else:
             Domoticz.Debug("Off cmd when ADB offline")

    if (self.isConnected >= 1):
     if (Unit == 2):  # Source
        if (Command == 'Set Level'):
            ase = 'Sources'
            cmdl = ""
            if self.cfg.has_section(ase):
             ops = self.cfg.options(ase)
             cmdc = 0
             for o in ops:
              cmdl = self.cfg.get(ase,o,raw=True)
              cmdc += 10
              if cmdc >= Level:
               break
            try:
              cmd = ["adb", "-s", self.config["host"]+":"+str(self.config["port"])]
              cmd2 = cmdl.split()
              cmd += cmd2
              subprocess.run(cmd, timeout=2 )
            except:
              pass
     if (Unit == 3):  # Volume
        if (Command == 'Set Level'):
              try:
               cmdv = cmdConnect + "shell cmd media_session volume --show --set " + str(Level)
               result1 = subprocess.run([cmdv], shell=True, capture_output=True, text=True, timeout=2)
               if int(Level) == 0:
                ml = 0
               else:
                ml = 1
               Devices[3].Update(nValue=ml,sValue=str(Level))
              except:
               pass
        elif Command == "Off": #mute
            try:
             cmdv = cmdConnect + "shell input keyevent 164"
             result1 = subprocess.run([cmdv], shell=True, capture_output=True, text=True, timeout=2)
            except:
             pass
        elif Command == "On": #unmute
            try:
             cmdv = cmdConnect + "shell input keyevent 164"
             result1 = subprocess.run([cmdv], shell=True, capture_output=True, text=True, timeout=2)
            except:
             pass
     if (Unit == 5):  # Apps
        if (Command == 'Set Level'):
            ase = 'Apps'
            cmdl = ""
            if self.cfg.has_section(ase):
             ops = self.cfg.options(ase)
             cmdc = 0
             for o in ops:
              cmdl = self.cfg.get(ase,o,raw=True)
              cmdc += 10
              if cmdc >= Level:
               break
            try:
              cmd = cmdConnect+cmdl
              result1 = subprocess.run([cmd], shell=True, capture_output=True, text=True, timeout=2)
            except:
              pass
     if (Unit == 6):  # Remote
        if (Command == 'Set Level'):
            ase = 'Remote'
            cmdl = ""
            if self.cfg.has_section(ase):
             cmdc = 0
             ops = self.cfg.options(ase)
             for o in ops:
              cmdl = self.cfg.get(ase,o,raw=True)
              cmdc += 10
              if cmdc >= Level:
               break
            try:
              subprocess.run(["adb", "-s", self.config["host"]+":"+str(self.config["port"]),"shell","input","keyevent",cmdl], timeout=2 )
            except:
              pass

    return True

 def onHeartbeat(self):
     Domoticz.Debug("Heartbeating...")
     cmdConnect = "adb -s "+Parameters["Address"]+":"+Parameters["Port"]+" "
     if self.initialized==0:
      self.isConnected = 0
      return False
     self._isAlive()
     currentStatus = 0
     if self.isConnected == 1:
      try:
       subprocess.run(["adb", "connect", self.config["host"]+":"+str(self.config["port"])], timeout=1 )
      except:
       pass
     elif self.isConnected == 2:
      try:
       log = str(subprocess.check_output("adb -s "+self.config["host"]+":"+str(self.config["port"])+ " shell dumpsys power |grep 'mWakefulness'", shell=True, timeout=2))
       if "Asleep" not in log: #screen is on and active (also screensaver)
         currentStatus = 1
       elif "error:" in log:
        self.isConnected = 1
      except:
       self.isConnected = 1

#Get current volume status
      if self.isConnected==2:
       try:
        log = str(subprocess.check_output("adb -s "+self.config["host"]+":"+str(self.config["port"])+ " shell media volume --get", shell=True, timeout=2))
       except:
        log = "error:"
       if ("error:" in log):
        self.isConnected = 1
       elif "volume" in log:
        sl = log.find('volume is')
        if sl>-1:
         ts = log[(sl+10):]
         ta = ts.split(" ")
         try:
          self.volume = int(float(ta[0].strip()))
          if self.volume == 0:
           ml = 0
          else:
           ml = 1
          try:
           av = int(Devices[3].sValue)
          except:
           av = -1
          if av != int(self.volume):
           Devices[3].Update(nValue=ml,sValue=str(self.volume))
         except:
          pass

#see which app is active (App text device 4 and Selector Switch 5)
      if self.isConnected>=1:
       try:
        log = str(subprocess.check_output("adb -s "+self.config["host"]+":"+str(self.config["port"])+ " shell dumpsys activity |grep -E 'mCurrentFocus'", shell=True, timeout=2))
        Domoticz.Log(log)
       except Exception as e:
        log = "error: "+str(e)
       if ("error:" in log):
        self.isConnected = 1
       elif "Focus" in log:
        try:
          current_focus = re.search(r'(\b\S+\/\S+\b)', log, re.IGNORECASE).group(0)

          ase = 'Apps'
          cmdl = ""
          if self.cfg.has_section(ase):
           ops = self.cfg.options(ase)
           cmdc = 0
           for o in ops:
            cmdl = self.cfg.get(ase,o,raw=True)
            #find the activity from the list in the database
            ret=re.split("shell am start -n|shell monkey -p|-c|/", cmdl)
            cmdc += 10
            if (str(ret[1]).strip() in str(current_focus).strip()):
             try:
               if str(Devices[5].sValue).strip() != str(cmdc): # Updating Selector Switch
                 Devices[5].Update(nValue=1,sValue=str(cmdc))
               if str(Devices[4].sValue).strip() != str(o).strip(): # Updating Text device with App name
                 Devices[4].Update(nValue=1,sValue=str(o).strip())
             except:
               pass

        except:
         current_focus = "" #TV probably off
         if str(Devices[4].sValue).strip() != "Off": # Updating Text device with App name
            Devices[4].Update(nValue=1,sValue="Off")

#Power on or Off
     if currentStatus == 0:
      if Devices[1].nValue != currentStatus:
       Devices[1].Update(nValue=0,sValue="Off")
       Devices[2].Update(nValue=0,sValue="Off")
       Devices[3].Update(nValue=0,sValue="Off")
       Devices[5].Update(nValue=0,sValue="0")
       Devices[6].Update(nValue=0,sValue="Off")
     else:
      if Devices[1].nValue != currentStatus:
       Devices[1].Update(nValue=1,sValue="On")
       Devices[2].Update(nValue=1,sValue="On")
       Devices[3].Update(nValue=1,sValue="On")
       Devices[5].Update(nValue=1,sValue="On")
       Devices[6].Update(nValue=1,sValue="On")
     return True

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    return

def onDeviceModified(Unit):
    global _plugin
    return

def onDisconnect(Connection):
    global _plugin
    return

def onMessage(Connection, Data):
    global _plugin
    return

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
    
