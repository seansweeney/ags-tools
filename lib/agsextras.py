# Client-side http
import httplib
# url fetch
import urllib
# json encode/decode
import json

# A function to generate a token given username, password and the adminURL.
def getToken(username, password, serverName, serverPort):
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"
    
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    
    # Connect to URL and post parameters
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", tokenURL, params, headers)
    
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
# This will help us distinguis any errors on the calling side
class RequestException(Exception):
    pass

class JsonErrorException(Exception):
    pass


# Perform a request
def sendRequest(serverName, serverPort, reqURL, params, headers):
    httpConn = httplib.HTTPConnection(serverName, serverPort)
    httpConn.request("POST", reqURL, params, headers)

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

