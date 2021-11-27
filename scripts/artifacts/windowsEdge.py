import os
import pyesedb
import struct
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

# https://gist.github.com/NotWearingPants/d162aaf32aef0227bf6bbd37b7317633
FILE_TIME_EPOCH = datetime.datetime(1601, 1, 1)
FILE_TIME_MICROSECOND = 10

def u64(x):
    return struct.unpack("<Q", x)[0]

def get_data(categoryName, record):
    accessCount = int.from_bytes(record.get_value_data(8), 'little')
    syncTime = convert_from_file_time(record.get_value_data(9))
    creationTime = convert_from_file_time(record.get_value_data(10))
    expiryTime = convert_from_file_time(record.get_value_data(11))
    modifiedTime = convert_from_file_time(record.get_value_data(12))
    accessedTime = convert_from_file_time(record.get_value_data(13))
    url = record.get_value_data(17).decode("utf-16")
    filename = record.get_value_data(18)
    return (categoryName, filename, url, accessCount, creationTime, modifiedTime, accessedTime, expiryTime, syncTime)

def convert_from_file_time(file_time):
    file_time = int.from_bytes(file_time, 'little')
    microseconds_since_file_time_epoch = file_time // FILE_TIME_MICROSECOND
    return FILE_TIME_EPOCH + datetime.timedelta(microseconds=microseconds_since_file_time_epoch)

def get_windowsEdge(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == "WebCacheV01.dat":
            continue

        file_object = open(file_found, "rb")
        esedb_file = pyesedb.file()
        esedb_file.open_file_object(file_object)
        ContainersTable = esedb_file.get_table_by_name("Containers")

        if ContainersTable.number_of_records > 0:

            report = ArtifactHtmlReport("WebCacheV01.dat")
            report.start_artifact_report(report_folder, 'WebCacheV01.dat')
            report.add_script()

            data_list = []

            data_headers = ('Category', 'Filename', 'Url', 'AccessCount', 'CreationTime', 'ModifiedTime', 'AccessedTime', 'ExpiryTime', 'SyncTime')

            for record in ContainersTable.records:
                containerId = u64(record.get_value_data(0))
                categoryName = record.get_value_data(8).decode("utf-16")

                if categoryName.startswith("History") or categoryName.startswith("MSHist"):
                    containerObject = esedb_file.get_table_by_name("Container_{}".format(containerId))
                    
                    for container in containerObject.records:
                        data_list.append(get_data(categoryName, container))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            tsvname = f'WebCacheV01.dat'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc(f"No Containers table available")
        
        file_object.close()