#!/usr/bin/python
import base64
import sys
import os
from pyzabbix import ZabbixAPI

# reading password from file
passfile = open('/home/dotza/python/base/password', 'r')
passw = passfile.readlines()
passw = base64.b64decode(passw[0].rstrip())

# Initializing ZabbixAPI
zapi = ZabbixAPI("http://monitor.st65.ru")
zapi.login("i.kim", passw)
print "Connected to Zabbix API Version %s" % zapi.api_version()


# Defining function which checks certain subnet
def check_subnet(subnet):
    # spliting input into 4 octets
    octets = subnet.split('.')
    result = ''
    for x in range(2, 255):
        ip = octets[0] + '.' + octets[1] + '.' + octets[2] + '.' + str(x)
        # pinging host
        if os.system('ping -c 2 -W 1 ' + ip + ' > /dev/null') == 0:
            hosts_counter = 0
            # if host is pingabe - check how many
            # instances of this host are in Zabbix
            for host in zapi.hostinterface.get(output="extend",
                                               filter={"ip": ip}):
                hid = host['hostid']
                hosts_counter += 1
            # Based on how many active instances of host there are in Zabbix -
            # print notification, or move to the next
            if hosts_counter == 0:
                result += ip + " is not in Zabbix!\n"
            elif hosts_counter == 1:
                # check if host is activated
                for j in zapi.host.get(output="extend",
                                       filter={"hostid": hid,
                                               "status": '1'}):
                    result += ip + " is not activated in Zabbix!\n"
            elif hosts_counter > 1:
                result += ("There are multiple instances of " + ip +
                           " in Zabbix!\n")
    return result

# Check number of arguments
if len(sys.argv) > 1:
    # Run Function Check_subnet() for each subnet in arguments
    for ind in range(1, len(sys.argv)):
        print 'checking subnet ' + str(sys.argv[ind])
        print check_subnet(str(sys.argv[ind]))
else:
    print "There is no argument"
