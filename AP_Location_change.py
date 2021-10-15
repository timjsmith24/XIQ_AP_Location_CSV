#!/usr/bin/env python3
import requests
import pandas as pd
import json
from requests.exceptions import HTTPError

BASEURL = "https://api.extremecloudiq.com"

HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

## TOKEN permission needs - "permissions": [ "device" ]
XIQ_token = 'xxx'
HEADERS["Authorization"] = "Bearer " + XIQ_token

rest = {
    "devices": "/devices/"
}

filename = 'apinfo.csv'

# Global Objects
pagesize = '100' #Value can be added to set page size. If nothing in quotes default value will be used (10)
totalretries = 5 #Value can be adjusted - this will adjust how many attempts to try each API call if any failures
device_list = [] #stores information about devices pulled for XIQ


# function that does get API call with the provided url (used to collect xiq devices)
def get_api_call( url, page=1, pageCount=1):
    ## used for page if pagesize is set manually
    flags = 0
    if page > 1:
        url = '{}?page={}'.format(url, page)
        flags = 1
    if pagesize:
        if flags == 0:
            url = "{}?limit={}".format(url, pagesize)
        else:
            url = "{}&limit={}".format(url, pagesize)
    ## the first call will not show as the data returned is used to collect the total count of Clients which is used for the page count
    #print(f"####{url}####")
    if pageCount > 1:
        print("API call on page {:>2} of {:2}".format(page, pageCount), end=": ")
    else:
        print("Attemping call", end=": ")
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
    except HTTPError as http_err:
        raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            log_msg = "Error retrieving devices from XIQ - no response!"
            #logging.error(log_msg)
            raise TypeError(log_msg)
        elif response.status_code != 200:
            log_msg = f"Error retrieving devices from XIQ - HTTP Status Code: {str(response.status_code)}"
            #logging.error(f"Error retrieving PPSK users from XIQ - HTTP Status Code: {str(response.status_code)}")
            #logging.warning(f"\t\t{response.json()}")
            raise TypeError(log_msg)

        rawList = response.json()
        if 'error' in rawList:
            if rawList['error_mssage']:
                failmsg = (f"Status Code {rawList['error_id']}: {rawList['error_message']}")
                raise ValueError(f"API Failed with reason: {failmsg} - on API {url}")
        return rawList


def put_api_call(url, locationid):
    print("Attemping call", end=": ")
    try:
        payload = json.dumps({"location_id": locationid,"x": 0,"y": 0})
        response = requests.put(url, headers=HEADERS, data= payload, timeout=20)
    except HTTPError as http_err:
        raise HTTPError(f'HTTP error occurred: {http_err} - on API {url}')  
    except Exception as err:
        raise TypeError(f'Other error occurred: {err}: on API {url}')
    else:
        if response is None:
            log_msg = "Error adding location to device from XIQ - no response!"
            #logging.error(log_msg)
            raise TypeError(log_msg)
        elif response.status_code != 200:
            log_msg = f"Error adding location to device from XIQ - HTTP Status Code: {str(response.status_code)}"
            #logging.error(f"Error retrieving PPSK users from XIQ - HTTP Status Code: {str(response.status_code)}")
            #logging.warning(f"\t\t{response.json()}")
            raise TypeError(log_msg)
        return 1

def getDevices():
    global device_list
    page = 1
    pageCount = 1
    firstCall = True
    success = 0
    url = BASEURL + rest['devices']
    while page <= pageCount:
        for count in range(1, totalretries+1):  
            try:
                data = get_api_call(url,page,pageCount)
            except TypeError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except ValueError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except HTTPError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with HTTP Error {e}")
            except:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")		
            else:
                print("Successful Connection")
                success = 1
                break
                #print(data['pagination'])
        if success != 1:
            print("Failed to collect devices")
            raise SystemExit
        # get paging information from result data
        if firstCall == True: 
            pageCount = data['total_pages']
            firstCall = False
        page += 1
        # collect relevant data from result data
        for device in data['data']:
            device = {
                "id":device['id'],
                "name":device['hostname'],
                "serialNumber":device['serial_number']
            }
            device_list.append(device)
    return device_list

def main():
    # loads csv data into df dataframe
    df = pd.read_csv(filename, dtype={'AP Serial': str})
    # add a new column for AP id in df
    df['apid'] = ""

    device_list = getDevices()
    #convert device_list to pandas dictionary
    device_df = pd.DataFrame(device_list)
    
    # iterate through df using the serial number to get the device id from the device_df. 
    # Using the AP id and the Location id (from csv) an API call is done per device in the csv file
    for index, row in df.iterrows():
        ap_serial = (row['AP Serial'])
        loc_id = (row["Location id"])
        filt = device_df['serialNumber'] == ap_serial
        apid = device_df.loc[filt,'id'].values[0]
        df.loc[index, 'apid'] = apid

        url = BASEURL + rest['devices'] + str(apid) + "/location"
        success = 0
        for count in range(1, totalretries+1):
            try:
                success = put_api_call(url, locationid=int(loc_id))
            except TypeError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except ValueError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with {e}")
            except HTTPError as e:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with HTTP Error {e}")
            except:
                print("Failed Connection")
                print(f"API failed attempt {count} of {totalretries} with unknown API error:\n 	{url}")		
            else:
                print("Successful Connection")
                break
        if success != 1:
            print("Failed to set location for devices")
            raise SystemExit
    #print(df)
        

if __name__ == '__main__':
	main()

