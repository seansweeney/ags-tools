#! python

# url fetch
import urllib

# System libraries
import sys

# Command line args
import argparse

# Common arcgis server functions
from agsextras import getArgs, getToken, readList, RequestException, JsonErrorException, sendRequest

def main(argv=None):
    # Create the parser object here and pass it in so script-specific arguments can be added if necessary
    parser = argparse.ArgumentParser()
    # Add script-specific arguments before passing in the parser
    args = getArgs(parser)

    # These may be configuration dependant.
    # Can add args above if necessary
    folder = 'root'

    stopList = readList(args.filename)

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

    # The requests used below only need the token and the response formatting parameter (json)
    body = urllib.urlencode({'token': token, 'f': 'json'})
    # The request headers are also fixed
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # Loop through each service in the list and stop
    for fullSvcName in stopList:
        print "Stopping: " + fullSvcName

        # Construct URL to get the status, then make the request
        reqURL = "/arcgis/admin/services/" + folder + fullSvcName + "/stop"
        # Post the request
        try:
            data = sendRequest(args.server, args.serverport, reqURL, body, headers)
        except RequestException:
            print "Error while stopping " + fullSvcName
            return
        except JsonErrorException as e:
            print "Error returned when extracting status information for " + fullSvcName + "."
            print str(e)
            return

    return

# Script start
if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
