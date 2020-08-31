# Client-side https
import httplib
import ssl
# url fetch
import urllib
# json encode/decode
import json

# System libraries
from os import environ

# Command line args
import argparse

# Prompt for password without echoing
import getpass

# Function to parse the command line and return the standard arguments
def getArgs(parser):
    parser.add_argument('-s', '--server', required=True, help='Server name')
    parser.add_argument('-u', '--user', required=False, help='User name')
    parser.add_argument('-p', '--password', required=False, help='Password')
    parser.add_argument('-f', '--filename', required=False, help='Output file name', default=environ['TEMP'] + '\\agsstarted.txt')
    parser.add_argument('--serverport', required=False, help='Server port', default='6080')

    args = parser.parse_args()

    # Prompt for username if not provided
    if not args.user:
        args.user = raw_input("Enter user name: ")

    # Prompt for password using getpass if not provided
    if not args.password:
        args.password = getpass.getpass("Enter password: ")

    return args

# A function to generate a token given username, password and the adminURL.
# TODO: Refactor to use sendRequest function
def getToken(username, password, serverName, serverPort):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"

    body = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # Connect to URL and post parameters
    if serverPort == '6080':
        httpConn = httplib.HTTPConnection(serverName, serverPort)
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) # Force TLS 1.2
        httpConn = httplib.HTTPSConnection(serverName, serverPort, context=context)
    httpConn.request("POST", tokenURL, body, headers)

    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Error while fetching tokens from admin URL. Please check the URL and try again."
        return
    else:
        data = response.read()
        httpConn.close()

        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return

        # Extract the token from it
        token = json.loads(data)
        return token['token']

# Define some custom exception classes for sendRequest
# This will help us distinguish any errors on the calling side
class RequestException(Exception):
    pass

class JsonErrorException(Exception):
    pass

# Perform a request
def sendRequest(serverName, serverPort, reqURL, body, headers):
    if serverPort == '6080':
        httpConn = httplib.HTTPConnection(serverName, serverPort)
    else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) # Force TLS 1.2
        httpConn = httplib.HTTPSConnection(serverName, serverPort, context = context)
    httpConn.request("POST", reqURL, body, headers)

    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        raise RequestException('Invalid response from request.')

    respData = response.read()

    # Done with the connection - close before error checking
    httpConn.close()

    # Check that data returned is not an error object
    if not assertJsonSuccess(respData):
        raise JsonErrorException(str(respData))

    # Deserialize response into Python object
    data = json.loads(respData)
    return data

# A function that checks that the input JSON object
#  is not an error object.
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True

# Serialize a list to disk
def saveList(data,filename):
    f = open(filename,'w') # Overwrites (truncates) existing
    json.dump(data,f)
    f.close()
    return True

# Read a serialized list from disk
def readList(filename):
    with open (filename) as f:
        fc = json.load(f)

    return fc

