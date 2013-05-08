#! python

# Client-side http
import httplib
# url fetch
import urllib
# json encode/decode
import json

# System tools
import sys, datetime   
from os import environ

# Command line args
import argparse 

# Prompt for password without echoing
import getpass 

# Common arcgis server functions
from agsextras import getToken, assertJsonSuccess, saveList, readList

def main(argv=None):
    # Setup the command line argument parser and parse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', required=True, help='Server name')
    parser.add_argument('-u', '--user', required=False, help='User name')
    parser.add_argument('-p', '--password', required=False, help='Password')
    parser.add_argument('-f', '--filename', required=False, help='Output file name', default=environ['TEMP'] + '\\agsstarted.txt')

    args = parser.parse_args()

    # Prompt for username if not provided
    if args.user:
        username = args.user
    else:
        username = raw_input("Enter user name: ")
        
    # Prompt for password using getpass if not provided
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("Enter password: ")
   
    serverName = args.server
    filename = args.filename

    # These may be configuration dependant.
    # Can add args above if necessary
    serverPort = 6080
    folder = 'root'

    # Keep track of the started services
    startedList = []
    
    # Get a token
    token = getToken(username, password, serverName, serverPort)
    if token == "":
        print "Could not generate a token with the username and password provided."
        return
    
    # Construct URL to read folder - handles folders other than root for future enhancement
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"
            
    folderURL = "/arcgis/admin/services/" + folder
    
    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters    
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", folderURL, params, headers)
    
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read folder information."
        return
    else:
        data = response.read()
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print "Error when reading folder information. " + str(data)

        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()

        # Loop through each service in the folder and get the status
        for item in dataObj['services']:

            fullSvcName = item['serviceName'] + "." + item['type']

            # Construct URL to get the status, then make the request                
            statusURL = "/arcgis/admin/services/" + folder + fullSvcName + "/status"
            httpConn.request("POST", statusURL, params, headers)
            
            # Read status response
            statusResponse = httpConn.getresponse()
            if (statusResponse.status != 200):
                httpConn.close()
                print "Error while checking status for " + fullSvcName
                return
            else:
                statusData = statusResponse.read()
                              
                # Check that data returned is not an error object
                if not assertJsonSuccess(statusData):
                    print "Error returned when retrieving status information for " + fullSvcName + "."
                    print str(statusData)
                else:
                    # Add the started service to a list
                    statusDataObj = json.loads(statusData)
                    if statusDataObj['realTimeState'] == "STARTED":
                        startedList.append(fullSvcName)
                        # Construct the URL to stop the service then make the request
                        stopURL = "/arcgis/admin/services/" + folder + fullSvcName + "/stop"
                        httpConn.request("POST", stopURL, params, headers)

                        # Read the status response
                        statusResponse = httpConn.getresponse()
                        if (statusResponse.status != 200):
                            httpConn.close()
                            print "Error while checking status for " + fullSvcName
                            return
                        else:
                            statusData = statusResponse.read()
                            if not assertJsonSuccess(statusData):
                                print "Error returned when stopping " + fullSvcName + "."
                                print str(statusData)
            httpConn.close()           

    # Check number of started services found
    if len(startedList) == 0:
        print "No started services detected in folder " + folder.rstrip("/")
    else:
        # Write out all the started services found
        # This could alternatively be written to an e-mail or a log file
        saveList(startedList, filename)
        print '\n'.join(startedList)

    return

# Script start
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
