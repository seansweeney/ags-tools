#! python

# url fetch
import urllib

# System libraries
import sys

# Command line args
import argparse

# Common arcgis server functions
from agsextras import getArgs, getToken, saveList, RequestException, JsonErrorException, sendRequest

def main(argv=None):
    # Create the parser object here and pass it in so script-specific arguments can be added if necessary
    parser = argparse.ArgumentParser()
    # Add script-specific arguments before passing in the parser
    args = getArgs(parser)

    # These may be configuration dependant.
    # Can add args above if necessary
    folder = 'root'

    # Keep track of the started services
    startedList = []

    # Get a token
    token = getToken(args.user, args.password, args.server, args.serverport)
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
    for item in data['services']:
        fullSvcName = item['serviceName'] + "." + item['type']

        # Construct URL to get the status, then make the request
        reqURL = "/arcgis/admin/services/" + folder + fullSvcName + "/status"
        # Post the request
        try:
            data = sendRequest(args.server, args.serverport, reqURL, body, headers)
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
                sendRequest(args.server, args.serverport, reqURL, body, headers)
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
        saveList(startedList, args.filename)
        print '\n'.join(startedList)

    return

# Script start
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
