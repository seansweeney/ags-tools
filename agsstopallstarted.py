#! python

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
from agsextras import getToken, saveList, readList, RequestException, JsonErrorException, sendRequest

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
            
    reqURL = "/arcgis/admin/services/" + folder
    
    # The requests used below only need the token and the response formatting parameter (json)
    params = urllib.urlencode({'token': token, 'f': 'json'})
    # The request headers are also fixed
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Post the request
    try:
        data = sendRequest(serverName, serverPort, reqURL, params, headers)
    except RequestException:
        print "Could not read folder information."
        return
    except JsonErrorException as e:
        print "Error when reading folder information. " + str(e)
        return

    # Loop through each service in the folder and get the status
    for item in data['services']:
        fullSvcName = item['serviceName'] + "." + item['type']

        # Construct URL to get the status, then make the request                
        reqURL = "/arcgis/admin/services/" + folder + fullSvcName + "/status"
        # Post the request
        try:
            data = sendRequest(serverName, serverPort, reqURL, params, headers)
        except RequestException:
            print "Error while checking status for " + fullSvcName
            return
        except JsonErrorException as e:
            print "Error returned when extracting status information for " + fullSvcName + "."
            print str(e)
            return

        if data['realTimeState'] == "STARTED":
            startedList.append(fullSvcName)
            # Construct the URL to stop the service then make the request
            reqURL = "/arcgis/admin/services/" + folder + fullSvcName + "/stop"

            # Post the request
            try:
                print "Stopping: " + fullSvcName
                # Don't need to restore the returned data for this request
                # All we get out of it is status which is handeled in the called function
                sendRequest(serverName, serverPort, reqURL, params, headers)
            except RequestException:
                print "Request error while stopping " + fullSvcName
                return
            except JsonErrorException as e:
                print "Error returned when stopping " + fullSvcName + "."
                print str(e)
                return

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
