# Update AP Location from CSV
## AP_Location_change.py
### Purpose
This script will read in a csv containing AP Serial,Location id. The Location id can be gathered using the https://api.extremecloudiq.com/locations/tree API call. 
Once csv is read in the script will make API calls gathering all devices in XIQ. Then will use the API Serials read in to get the id of the device. Then will do an API call to update the device's location with the location id read in from the CSV

## User Input Data
#### XIQ token
A XIQ token will need to be generated with minimum of the below permissions and added to the script. This can be done using the [Swagger page](https://api.extremecloudiq.com/swagger-ui/index.html?configUrl=/openapi/swagger-config#/).

```
"permissions": [
    "device"
  ]
```

###### lines 12
```
XIQ_token = 'xxx'
```

Other variables that can be adjusted
###### lines 22 -23
```
pagesize = '100' #Value can be added to set page size. If nothing in quotes default value will be used (10)
totalretries = 5 #Value can be adjusted - this will adjust how many attempts to try each API call if any failures
```


#### AP info
The AP serial numbers and new location ids will need to be put in the apinfo.csv. The header line in the csv needs to be as below or script will not function
```
AP Serial,Location id
01301505040168,769490635818704
03051912090116,769490635818704
```

## Script Outputs
The script will print a line per API call, adding a success or failure (with message)
```
Attemping call: Successful Connection
```

## Requirements
This script was written for Python3.6 or higher. The requests and pandas modules will need to be installed in order for the script to function. This modules are listed in the requirements.txt file and can be easily installed with pip.
```
pip install -r requirements.txt
``` 