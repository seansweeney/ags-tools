# ags-tools

Python scripts and library module for mananging ArcGIS Server 10.1 map services.

## Included scripts

* lib/agsextras.py - module containing common definitions
* agsstopallstared.py - script to stop all started services
* agsstatusfromlist.py - script to get the status of all the services in a given list
* agsstartfromlist.py - script to start all the services in a given list

## Using the scripts

### Setup

Be sure to add the lib directory to your PYTHONPATH.  To make the scripts easier to run in Windows you can also add '.PY' to your PATHEXT and add the script directory to your PATH.

### Common Arguments
-s SERVER

    The ArgGIS Server name.

--serverport SERVERPORT

   	Optional server port.
    Default: 6080

-u USER

    Username for an authorized admin user.  If left out the scripts will prompt for it.

-p PASSWORD

    Password for the authorized admin user.  If left out the scripts will prompt for it using getpass to mask the input
  
-f FILENAME

    Optional file for inputting or outputting a list of services to manage.
    Default: environ['TEMP'] + '\\agsstarted.txt'

### agsstopstarted.py
Query the server for started services, stop all of them, and write a list to disk for later re-starting.

```PowerShell
agsstopallstarted.py [-h] -s SERVER [-u USER] [-p PASSWORD]
                     [-f FILENAME] [--serverport SERVERPORT]
```

### agsstatusfromlist.py
Get the status of the services listed in the given file.  This is a useful double-check after starting the services from the list.

```PowerShell
agsstatusfromlist.py [-h] -s SERVER [-u USER] [-p PASSWORD]
                     [-f FILENAME] [--serverport SERVERPORT]
```

### agsstartfromlist.py
Start the services listed in the given file.

```PowerShell
agsstartfromlist.py [-h] -s SERVER [-u USER] [-p PASSWORD]
                    [-f FILENAME] [--serverport SERVERPORT]
```
