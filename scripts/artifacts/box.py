import os
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_box(files_found, report_folder, seeker, wrap_text):
    streemfs_db = ''
    sync_db = ''
    source_file_streemfs = ''
    source_file_sync = ''

    for file_found in files_found:
        
        if file_found.endswith("streemfs.db"):
            streemfs_db = str(file_found)
            source_file_streemfs = file_found.replace(seeker.directory, '')

        elif file_found.endswith("sync.db"):
            sync_db = str(file_found)
            source_file_sync = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(streemfs_db)
    cursor = db.cursor()
    try:
        cursor.execute('''select 
            CASE 
            WHEN fsnodes.isFile = 0 THEN 'No'
            WHEN fsnodes.isFile = 1 THEN 'Yes'
            ELSE 'Unknown'
            END AS isFile,
            fsnodes.name AS name,
            datetime(fsnodes.createdAtTimestamp, 'unixepoch', 'localtime') AS createdAtTimestamp,
            datetime(fsnodes.modifiedAtTimestamp, 'unixepoch', 'localtime') AS modifiedAtTimestamp,
            datetime(fsnodes.accessedAtTimestamp, 'unixepoch', 'localtime') AS accessedAtTimestamp,
            datetime(fsnodes.lastUsedTime, 'unixepoch', 'localtime') AS lastUsedTime,
            datetime(fsnodes.folderFetchTimestamp, 'unixepoch', 'localtime') AS folderFetchTimestamp
            from fsnodes ORDER BY fsnodes.createdAtTimestamp desc
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('Box - fsnodes')
        report.start_artifact_report(report_folder, 'Box - fsnodes')
        report.add_script()
        data_headers = ('isFile', 'name', 'createdAtTimestamp', 'modifiedAtTimestamp', 'accessedAtTimestamp', 'lastUsedTime', 'folderFetchTimestamp')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6]))

        report.write_artifact_data_table(data_headers, data_list, streemfs_db)
        report.end_artifact_report()

        tsvname = f'Box - fsnodes'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_streemfs)
    else:
        logfunc('No streemfs.db - fsnodes available')

    db.close()

    db = open_sqlite_db_readonly(sync_db)
    cursor = db.cursor()
    try:
        cursor.execute('''select
            box_item.name AS name,
            box_item.sort_name AS sort_name,
            box_item.size AS size,
            datetime(box_item.content_created_at, 'unixepoch', 'localtime') AS content_created_at,
            datetime(box_item.content_updated_at, 'unixepoch', 'localtime') AS content_updated_at
            from box_item ORDER BY box_item.content_created_at desc
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('Box - box_item')
        report.start_artifact_report(report_folder, 'Box - box_item')
        report.add_script()
        data_headers = ('name', 'sort_name', 'size', 'content_created_at', 'content_updated_at')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4]))

        report.write_artifact_data_table(data_headers, data_list, sync_db)
        report.end_artifact_report()

        tsvname = f'Box - box_item'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_sync)
    else:
        logfunc('No sync.db - box_item available')

    db.close()