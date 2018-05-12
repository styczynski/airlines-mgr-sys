[![Made by Styczynsky Digital Systems][badge sts]][link styczynski]

[![Screenshot of webpage][screenshot1]](https://github.com/styczynski/airlines-mgr-sys)

# 📜 :airplane: The Airlines Manager System

  The purpose of this project completed as an assignment for 3W subject was to design Django system for managing airlines data.
  
## Requirements

This projects requires bash shell (or at least some kind of emulation) and Python 3.

**Note:**
If you want to use real-time server status updates you must have *Redis* database installed<br>
and available via *redis-server* command.

## Setup

  The *airm* performs auto-configuration and then run Django server at localhost:8000.
  To begin just type the following command into the bash shell:
  ```
  
  ./airm up
  
  ```
  
  Please enter all deails if prompted by the *airm*.
  
  Then wait for completion and navigate to `localhost:8000` to see the system's main page.
  
  **Please note:** in `airm` file you must specify python executable you are using (if it's not default *python* or *python3*)
  
## Advanced setup

  You can manually configure you virtual environment or use your global one:
  Execute the following command to install all requirements:
  
  ```
    pip install -r requirements.txt
  ```
  
## :airplane: *airm* commands

 Generator script `generate` supports the following commands:
 
 * **init**
 
          Automatically create virtual environment for execution
          Also make and migrate with Django.
          Skip if it actually exists.
 * **reset**
 
          Automatically create virtual environment for execution
          Override any previous one.
 * **server** (alias: **dev**)
 
          Run Django devserver at localhost:8000 with redis (if installed) and background task runner.
 * **up**
 
          Alias for executing setup and then server command
 
## Features

[![Screenshot of features][screenshot_features]](https://github.com/styczynski/airlines-mgr-sys)

* Sortable, filterable tables with all useful data
* Ability to add and remove users from flights
* Data generator to provide dummy names for the system
* Real-time server notification via Django Channels
 
[![Screenshot of webpage][screenshot2]](https://github.com/styczynski/airlines-mgr-sys)

[badge sts]: https://img.shields.io/badge/-styczynsky_digital_systems-blue.svg?style=flat-square&logoWidth=20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABYAAAAXCAYAAAAP6L%2BeAAAABmJLR0QA%2FwD%2FAP%2BgvaeTAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAB3RJTUUH4AgSEh0nVTTLngAAAB1pVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVBkLmUHAAAAm0lEQVQ4y2Pc%2Bkz2PwMNAAs2wVMzk4jSbJY%2BD6ccEwONACMsKIh1JSEgbXKeQdr4PO1cPPQMZiGkoC7bkCQD7%2Fx7znDn35AOClK9PEJSBbNYAJz999UGrOLocsM0KHB5EZ%2FXPxiVMDAwMDD8SP3DwJA6kFka5hJCQOBcDwMDAwPDm3%2FbGBj%2BbR8tNrFUTbiAB8tknHI7%2FuTilAMA9aAwA8miDpgAAAAASUVORK5CYII%3D

[link styczynski]: http://styczynski.in

[screenshot1]: https://raw.githubusercontent.com/styczynski/airlines-mgr-sys/master/static/screenshot.png

[screenshot2]: https://raw.githubusercontent.com/styczynski/airlines-mgr-sys/master/static/screenshot2.png

[screenshot_features]: https://raw.githubusercontent.com/styczynski/airlines-mgr-sys/master/static/screenshot_features.png

