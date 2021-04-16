# ADLSGen2UpdateMovedFile

## Synopsis
Recently, I got engaged with a data replication issue between two independant [Azure Data Lake Storage Gen2 (ADLS)](https://docs.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction) accounts with [Azure Data Factory (ADF)](https://docs.microsoft.com/en-us/azure/data-factory/). The intention replicating the data was to create a custom backup for the primary account.

There is a nice template available [here](https://docs.microsoft.com/en-us/azure/data-factory/solution-template-copy-new-files-lastmodifieddate) that will incrementally copy data based on their last modification time (LMT). In combination with the [tumbling window trigger](https://docs.microsoft.com/en-us/azure/data-factory/concepts-pipeline-execution-triggers#tumbling-window-trigger) of ADF, this will create a quite convenient approach to create backups incrementally.

We stumbled accross one issue though: when files in ADLS get moved to another folder or renamed, the LMT does not change. That is by design as the file itself indeed does not change. However, for the above mentioned scenario, this is not indented behavior and could lead to data loss in the worst case. 

To work around that behavior, I create this small [Azure Function](https://docs.microsoft.com/en-us/azure/azure-functions/), that will add useful custom metadata to the file, such as the time when it was moved and the original location. The update of custom metadata itself will change the LMT already, so we are good to go. The custom metadata could be useful anyway for a different usecase. 

The function is triggered when a file or folder has been moved automatically with usage of [Azure Event Grid](https://docs.microsoft.com/en-us/azure/event-grid/). It's a fairly easy process to setup as documented [here](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-event-overview). 

## Usage

1. Create the function app using the repo and configure all parameters that are required to authenticate to ADLS. I am using a SPN here, that comes with an application ID, a secret and belongs to an Azure Active Directory tenant that needs to be provided. The SPN needs according writing permissions on ADLS, to don't tell anyone about the credentials.

2. Create the Azure Eventgrid subscription for renaming events (moving is basically a renaming of the file path) for files and folders. Better start from the Storage Account view as it might be easier to setup everything. Point to the provisioned function.

That should be it already. 

## Disclaimer
This is a **sample script** that is covering the requirements for this particular scenario. It comes **WITHOUT ANY GUARANTEE** and is provided **AS-IS**. It is not very robust (no proper error handling, etc.) and might not cover additional backup requirements. It could even lead to data loss, so please use with caution. That's the nature of sample scripts!
