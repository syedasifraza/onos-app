#!/usr/bin/python

import sys, string, curl, pycurl, os
import json, cStringIO

topoApi="topology"
devicesApi="devices"
hostsApi="hosts"
intentsApi="intents"
ipAddress=None
username=None
password=None
hostsId=["0"]
intentsId=["0"]

def getRequest(method, restApi, post_data=None):

   global username,password,ipAddress

   response = cStringIO.StringIO()
   c = pycurl.Curl()

   if method == 'get':
      c.setopt(pycurl.HTTPGET, 1)
      c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])

   elif method == 'post':
      c.setopt(pycurl.POST, 1)
      c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
      c.setopt(pycurl.POSTFIELDS, post_data)

   elif method == 'delete':
      c.setopt(pycurl.CUSTOMREQUEST,"DELETE")

   else:
      c.setopt(pycurl.CUSTOMREQUEST, method.upper())

   c.setopt(pycurl.URL, 'http://'+ipAddress+':8181/onos/v1/'+restApi)
#   c.setopt(pycurl.URL, 'http://10.1.5.2:8181/onos/v1/topology')
#  c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
#   c.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json'])
   c.setopt(c.WRITEFUNCTION, response.write)
   c.setopt(pycurl.USERPWD, username+ ':'+password)
   c.setopt(pycurl.CONNECTTIMEOUT, 3)
   try:
      c.perform()
   except pycurl.error:
      return 0,0
   rcode = c.getinfo(pycurl.RESPONSE_CODE)
   c.close()
   if method == 'post' or method == 'delete':
      return rcode
   else:
      rbody = json.loads(response.getvalue())
      return rcode, rbody
  

def getInfo():

   global topoApi,ipAddress,username,password

   while(True):
      ipAddress = raw_input("Please enter IP address of ONOS controller-->")
      username=raw_input("Please enter username--> ")
      password=raw_input("Please enter password--> ")
      os.system('clear')
      rcode, rbody = getRequest('get', topoApi)

      if(rcode!=200):
         responseError()

      else:
         break


def responseError():

   print "Error: something wrong in provide information!"
   print "Please enter correct information again...!!!"
   presskey()
   os.system('clear')


def getTopology():
   global topoApi

   rcode, getTopology = getRequest('get', topoApi)
   if(rcode != 200):
      resposeError()
   else:
      os.system('clear')
      i = 1
      for data in getTopology:
         value = getTopology[data]
         if data != 'time':
            print "{}. {} = {}".format(i,data,value)
            i = i + 1

def getDevices():
   global devicesApi

   rcode, getDevices = getRequest('get', devicesApi)
   if(rcode !=200):
      responseError()
   else:
      os.system('clear')
      i = 1
      jsonData = getDevices["devices"]
      for item in jsonData:
         print ("SWITCH #{}:".format(i))
         print ("\tAvailable: \t{} \n\tManufacturer: \t{} \n\tHardware: \t{} \n\tIP Address: \t{} \n\tProtocol: \t{} \n\tID: \t{}".format(item.get("available"),item.get("mfr"),item.get("hw"),item.get("annotations").get("managementAddress"),item.get("annotations").get("protocol"),item.get("id")))
         i = i + 1


def getHosts():

   global hostsApi,hostsId

   hostsId=["0"]
   rcode, getHosts = getRequest('get', hostsApi)
   if(rcode!=200):
     responseError()
   else:
      os.system('clear')
      i = 1
      jsonData = getHosts["hosts"]
      for item in jsonData:
         hostsId.append(item.get("id"))
         print ("HOSTS #{}:".format(i))
         print ("\tIP Addresses: \t{} \n\tMAC Address: \t{} \n\tVlan ID: \t{}".format(item.get("ipAddresses"),item.get("mac"),item.get("vlan")))
         i = i + 1


def enabledComm():

   global intentsApi,hostsId,intentsId
   k = 0
   intentsId=["0"]

   rcode, rbody = getRequest('get',intentsApi)
   if (rcode!=200):
      responseError()
   else:
      jsonData = rbody["intents"]
      for item in jsonData:
         k = k + 1
         ids=item.get("id")
         intentsId.append(ids)
         c_ids=[]
         i = 0
         ids=item.get("resources")
         for data in ids:
            c_ids.append(data)
         for hosts in hostsId:
            if c_ids[0]==hosts:
               one = i
            elif c_ids[1]==hosts:
               two = i

            i = i + 1
         print ("{}. Host #{}<------>Host #{}".format(k,one,two))


def deleteRule():

   global intentsApi,intentsId

   getHosts()
   enabledComm()
   while True:
      ruleNumber = input("Enter rule number to delete-->")
      if(ruleNumber==0 or ruleNumber>(len(intentsId)-1)):
         print "Error! wrong input provided..."
         presskey()
         deleteRule()
      else:
         break
#   intentsApi=intentsApi+'/org.onosproject.cli/'+intentsId[ruleNumber]
   rcode = getRequest('delete',intentsApi+'/org.onosproject.cli/'+intentsId[ruleNumber])
   if rcode == 204:
      print "Rule successfully deleted..."
      presskey()

   else:
      print "Error! rule not deleted..."
      presskey()


def enableComm():
   global intentsApi,hostsId

   getHosts()
   while True:
      one = input("Enter 1st HOST number-->")
      two = input("Enter 2nd HOST number-->")

      if (one==two or one==0 or one>(len(hostsId)-1) or two==0 or two>(len(hostsId)-1)):
         print "Wrong host number provided..."
         presskey()
         os.system('clear')
         getHosts()

      else:
        break

   data=('{"type":"HostToHostIntent","appId":"org.onosproject.cli","priority":55,"one":"'+hostsId[one]+'","two":"'+hostsId[two]+'"}')

   rcode = getRequest('post', intentsApi, data)

   if(rcode==201):
      print "Forwarding rule successfully added"
      presskey()
   else:
      print "Forwarding rule not added, please try again..."
      print rcode
      presskey()


def presskey():
   try:
      input ("Press [Enter] to continue...")
   except SyntaxError:
      pass


def mainMenu():

   while(True):
      os.system('clear')
      print "1. Show topology information."
      print "2. Show devices list."
      print "3. Show hosts list."
      print "4. Add new forwarding rule between two hosts."
      print "5. Delete forwarding rules of hosts."
      print "6. Show installed forwarding rules hosts."
      print "7. Exit."

      inputOpt=raw_input("Select your option []")

      if (inputOpt=="1"):
         os.system('clear')
         getTopology()
         presskey()

      elif (inputOpt=="2"):
         os.system('clear')
         getDevices()
         presskey()

      elif (inputOpt=="3"):
         os.system('clear')
         getHosts()
         presskey()

      elif (inputOpt=="4"):
         os.system('clear')
         enableComm()

      elif (inputOpt=="5"):
         getHosts()
         os.system('clear')
         deleteRule()
         presskey()

      elif (inputOpt=="6"):
         getHosts()
         os.system('clear')
         enabledComm()
         presskey()

      elif (inputOpt=="7"):
         os.system('clear')
         break

      else:
         os.system('clear')
         print "Wrong option selected..!!"

def main():
   os.system('clear')
   getInfo()
   mainMenu()
#   getRequest('get', 'test')
main()
              

