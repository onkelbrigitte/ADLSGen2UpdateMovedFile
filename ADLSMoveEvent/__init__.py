#basic imports
import json
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

#Azure specific imports
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import FileSystemClient, DataLakeFileClient

#Azure function specific import
import azure.functions as func

#this function will parse the request to get all relevant information from the Azure Eventgrid event
def parseRequest(event):

    #get event time for request body
    eventTime = str(event.event_time)

    #get URLs fform request body
    destinationURL = event.get_json()["destinationUrl"]
    sourceURL = event.get_json()["sourceUrl"]

    url_parsed = urlparse(destinationURL)
    url_parsed_path = url_parsed.path.split("/", 2)

    return {"account_url": url_parsed.hostname , "file_system_name":  url_parsed_path[1], "file_path": url_parsed_path[2], "eventTime":eventTime, "sourceURL": sourceURL }


def main(event: func.EventGridEvent):

    #get SPN info get authenticate against ADLS. Remember to configure these parameter in the configuration setting of your Azure function.
    tenantID = os.environ["credential_spn_tenantid"]
    clientID = os.environ["credential_spn_clientid"]
    clientSecret =  os.environ["credential_spn_secret"]

    #Set names for custom attributes
    property_name_LastmovedOn = "LastMovedOn"
    property_name_PreviousLocation = "PreviousLocationURL"

    #parse event data to determine account, filesystem and filepath as well as eventtime
    parsed_Request = parseRequest(event)

    #set parameters to update the file
    account_url = parsed_Request["account_url"]
    file_system_name = parsed_Request["file_system_name"]
    file_path = parsed_Request["file_path"]
    eventTime = parsed_Request["eventTime"]
    sourceURL = parsed_Request["sourceURL"]

    #create connectivity objects 
    identity = ClientSecretCredential(tenant_id=tenantID, client_id=clientID, client_secret=clientSecret )
    filesysclient = FileSystemClient(credential=identity, account_url= account_url, file_system_name = file_system_name)
    fileclient = filesysclient.get_file_client(file_path=file_path)

    #build updated metadata
    metadata = {property_name_LastmovedOn: eventTime, property_name_PreviousLocation: sourceURL}

    #set metadata
    fileclient.set_metadata(metadata=metadata)

    #close connection
    fileclient.close()





