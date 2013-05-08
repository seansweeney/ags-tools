# ags-tools

Python scripts for mananging ArcGIS Server 10.1 map services.

## Included scripts

* lib/agsextras.py - module containing common definitions
* agsstopallstared.py - script to stop all started services

## Using the scripts

### Setup

Be sure to add the lib directory to your PYTHONPATH.  To make the scripts easier to run in Windows you can also add '.PY' to your PATHEXT and add the script directory to your PATH.

### Common Arguments
-s SERVER

    The ArgGIS Server name.  Port 6080 is assummed in the current version.

-u USER

    Username for an authorized admin user.  If left out the scripts will prompt for it.

-p PASSWORD

    Password for the authorized admin user.  If left out the scripts will prompt for it using getpass to mask the input
  
-f FILENAME

    File for inputting or outputting a list of services to manage.
  
### agsstopstarted.py

```PowerShell
agsstopallstarted.py [-h] -s SERVER [-u USER] [-p PASSWORD]
                     [-f FILENAME]
```
