import os
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

# https://gist.github.com/gamesbook/03d030b7b79370fb6b2a67163a8ac3b5
def convert_dotnet_tick(ticks):
    """Convert .NET ticks to formatted ISO8601 time
    Args:
        ticks: integer
            i.e 100 nanosecond increments since 1/1/1 AD"""
    _date = datetime.datetime(1, 1, 1) + \
        datetime.timedelta(microseconds=ticks // 10)
    if _date.year < 1900:  # strftime() requires year >= 1900
        _date = _date.replace(year=_date.year + 1900)
    return _date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3]

def get_dropbox(files_found, report_folder, seeker, wrap_text):
    cachefiles_db = ''
    contacts_db = ''
    sync_history_db = ''
    source_file_cachefiles = ''
    source_file_contacts = ''
    source_file_sync_history = ''

    for file_found in files_found:
        
        if file_found.endswith("cachefiles.sqlite"):
            cachefiles_db = str(file_found)
            source_file_cachefiles = file_found.replace(seeker.directory, '')

        elif file_found.endswith("contacts.sqlite"):
            contacts_db = str(file_found)
            source_file_contacts = file_found.replace(seeker.directory, '')

        elif file_found.endswith("sync_history.db"):
            sync_history_db = str(file_found)
            source_file_sync_history = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(cachefiles_db)
    cursor = db.cursor()
    try:
        cursor.execute('''select 
            CacheItem.FileName AS FileName,
            CacheItem.Path AS Path,
            CacheItem.LocalFileSize AS Filesize,
            CacheItem.Hash AS Hash,
            CacheItem.LastAccessDateTime AS LastAccessDateTime,
            CacheItem.LocalLastModifiedTime AS LocalLastModifiedTime
            from CacheItem ORDER BY CacheItem.LastAccessDateTime desc
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('Dropbox App - CacheItem')
        report.start_artifact_report(report_folder, 'Dropbox App - CacheItem')
        report.add_script()
        data_headers = ('Filename', 'Path', 'Filesize', 'Hash', 'LastAccessDateTime', 'LocalLastModifiedTime')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3], convert_dotnet_tick(rows[4]), convert_dotnet_tick(rows[5])))

        report.write_artifact_data_table(data_headers, data_list, cachefiles_db)
        report.end_artifact_report()

        tsvname = f'Dropbox App - CacheItem'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_cachefiles)
    else:
        logfunc('No cachefiles.sqlite - CacheItem available')

    db.close()

    db = open_sqlite_db_readonly(contacts_db)
    cursor = db.cursor()
    try:
        cursor.execute('''select 
            ContactItem.Email AS Email,
            ContactItem.DBId AS DBId,
            ContactItem.PhotoUrl AS PhotoUrl,
            ContactItem.Name AS Name
            from ContactItem
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('Dropbox App - ContactItem')
        report.start_artifact_report(report_folder, 'Dropbox App - ContactItem')
        report.add_script()
        data_headers = ('Email', 'DBId', 'PhotoUrl', 'Name')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3]))

        report.write_artifact_data_table(data_headers, data_list, contacts_db)
        report.end_artifact_report()

        tsvname = f'Dropbox App - ContactItem'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_contacts)
    else:
        logfunc('No contacts.sqlite - ContactItem available')

    db.close()

    db = open_sqlite_db_readonly(sync_history_db)
    cursor = db.cursor()
    try:
        cursor.execute('''select 
            sync_history.event_type AS event_type,
            sync_history.file_event_type AS file_event_type,
            sync_history.direction AS direction,
            sync_history.local_path AS local_path,
            sync_history.other_user AS other_user,
            datetime(sync_history.timestamp, 'unixepoch', 'localtime') AS timestamp
            from sync_history ORDER BY timestamp desc
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('Dropbox - Sync History')
        report.start_artifact_report(report_folder, 'Dropbox - Sync History')
        report.add_script()
        data_headers = ('Event Type', 'File Event Type', 'Direction', 'local_path', 'other_user', 'timestamp')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5]))

        report.write_artifact_data_table(data_headers, data_list, sync_history_db)
        report.end_artifact_report()

        tsvname = f'Dropbox - Sync History'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_sync_history)
    else:
        logfunc('No sync_history.db - sync_history available')