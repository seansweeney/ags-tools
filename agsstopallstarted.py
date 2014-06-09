#! python

# url fetch
import urllib

# System libraries
import sys

# Command line args
import argparse

# json encode/decode
import json

# Common arcgis server functions
from agsextras import getArgs, getToken, saveList, RequestException, JsonErrorException, sendRequest

def main(argv=None):
    # Create the parser object here and pass it in so script-specific arguments can be added if necessary
    parser = argparse.ArgumentParser()
    # Add script-specific arguments before passing in the parser
    args = getArgs(parser)

    allfiles = allRootFiles(args) + allFolderFiles(args)
    
    # Keep track of the started services
    startedList = []

    # Get a token
    token = getToken(args.user, args.password, args.server, args.serverport)
    if token == "":
        print "Could not generate a token with the username and password provided."
        return
    
    reqURL = "/arcgis/admin/services/"

    # The requests used below only need the token and the response formatting parameter (json)
    body = urllib.urlencode({'token': token, 'f': 'json'})
    
    # The request headers are also fixed
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # Post the request
    try:
        data = sendRequest(args.server, args.serverport, reqURL, body, headers)
    except RequestException:
        print "Could not read folder information."
        return
    except JsonErrorException as e:
        print "Error when reading folder information. " + str(e)
        return

    # Loop through each service in the folder and get the status
    for item in allfiles:

        # Construct URL to get the status, then make the request
        reqURL = "/arcgis/admin/services/" + item + "/status"
        #print reqURL
        
        # Post the request
        try:
            data = sendRequest(args.server, args.serverport, reqURL, body, headers)
        except RequestException:
            print "Error while checking status for " + item
            return
        except JsonErrorException as e:
            print "Error returned when extracting status information for " + item
            print str(e)
            return

        if data['realTimeState'] == "STARTED":
            startedList.append(item)
            # Construct the URL to stop the service then make the request
            reqURL = "/arcgis/admin/services/" + item + "/stop"

            # Post the request
            try:
                print "Stopping: " + item
                # Don't need to restore the returned data for this request
                # All we get out of it is status which is handeled in the called function
                sendRequest(args.server, args.serverport, reqURL, body, headers)
                print sendRequest(args.server, args.serverport, reqURL, body, headers) 
            except RequestException:
                print "Request error while stopping " + item
                return
            except JsonErrorException as e:
                print "Error returned when stopping " + item
                print str(e)
                return

    # Check number of started services found
    if len(startedList) == 0:
        print "No started services detected in folder "
    else:
        # Write out all the started services found
        # This could alternatively be written to an e-mail or a log file
        saveList(startedList, args.filename)
        #print '\n'.join(startedList)

    return

# Recursively searches services within the ArcGIS Services folders

def allFolderFiles(args):
        # Locates the root arcgis services directory
        jsonData = urllib.urlopen('http://%s/arcgis/rest/services/?f=pjson' % args.server)

        # Opens the root arcgis directory
        data = json.load(jsonData)

        # Closes the root arcgis directory
        jsonData.close()

        # Counts the number of folders in the root directory
        numberOfFolders = len(data["folders"])
        allfiles = []
        
        # Inerates through each unique folder
        for index, folderName in enumerate(range(0,numberOfFolders)):
                try: 
                        #Fetches the 1st folder name out of the lenght of the array
                        folder = data["folders"][folderName]

                        # Locates arcgis services directory of that folder
                        jsonFolders = urllib.urlopen('http://%s/arcgis/rest/services/%s?f=pjson' % (args.server, folder))

                        # Opens the folder
                        individualFiles = json.load(jsonFolders)

                        # Closes folder
                        jsonFolders.close()
                except:
                        print 'Error within the folders'
                        
                # Counts the number of services within folder path 
                numberofFiles = len(individualFiles["services"])

                # Inerates through each unique services
                for index2, services in enumerate(range(0,numberofFiles)):
                        # Break for testing purposes only. Remove after testing is completed
                        try:
                                # Fetches the 1st services name out of the length of the array
                                if individualFiles["services"][services]['type'] == 'MapServer':
                                        nameAndType = individualFiles["services"][services]['name'] + "." + data["services"][services]['type']
                                        allfiles.append(nameAndType)
                                else:
                                        continue
                        except:
                                print 'Error within the files services'
        return allfiles

def allRootFiles(args):
        # Locates the root arcgis services directory
        jsonData = urllib.urlopen('http://%s/arcgis/rest/services/?f=pjson' % args.server)

        # Opens the root arcgis directory
        data = json.load(jsonData)

        # Closes the root arcgis directory
        jsonData.close()

        # Counts the number of folders in the root directory
        numberOfFolders = len(data["services"])

        # Inerates through each unique services
        allfiles = []
        for index2, services in enumerate(range(0,numberOfFolders)):
                try:
                        # Fetches the 1st services name out of the length of the array
                        if data["services"][services]['type'] == 'MapServer':
                                nameAndType = data["services"][services]['name'] + "." + data["services"][services]['type']
                                allfiles.append(nameAndType)
                        else:
                                continue
                except:
                        print 'Error within the files services'
        return allfiles


# Script start
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
