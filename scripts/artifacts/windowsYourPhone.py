import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_windowsYourPhone(files_found, report_folder, seeker, wrap_text):
    source_file_photos = ''
    source_file_phone = ''
    photos_db = ''
    phone_db = ''

    for file_found in files_found:
        
        if file_found.endswith("phone.db"):
            phone_db = str(file_found)
            source_file_phone = file_found.replace(seeker.directory, '')

        elif file_found.endswith("photos.db"):
            photos_db = str(file_found)
            source_file_photos = file_found.replace(seeker.directory, '')

    db = open_sqlite_db_readonly(phone_db)
    cursor = db.cursor()
    try:
        cursor.execute('''select 
        Contact.contact_id,
        contact.display_name,
        contact.alternative_name,
        contact.nicknames,
        case when contact.last_updated_time notnull then datetime((contact.last_updated_time /10000000)-11644473600, 'unixepoch','localtime') end as 'Last_Updated',
        address.address,
        address.address_type, 
        case address.is_primary when 0 then 'No' when 1 then 'Yes' end as 'Is_Primary',
        address.times_contacted,
        case when contact.last_contacted_time notnull then datetime((contact.last_contacted_time /10000000)-11644473600, 'unixepoch','localtime') end as 'Last_Contacted'

        from contact 
        left join address on  address.contact_id = contact.contact_id
        order by address.times_contacted desc''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('YourPhone - Contacts')
        report.start_artifact_report(report_folder, 'YourPhone - Contacts')
        report.add_script()
        data_headers = ('contact_id', 'display_name', 'alternative_name', 'nicknames', 'Last Updated', 'address', 'address_type', 'Is_Primary', 'times contacted', 'Last Contacted')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4], rows[5], rows[6], rows[7], rows[8], rows[9]))

        report.write_artifact_data_table(data_headers, data_list, phone_db)
        report.end_artifact_report()

        tsvname = f'YourPhone - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_phone)
    else:
        logfunc('No phone.db Contacts available')

    try:
        cursor.execute('''select message.Message_id as 'MessageID',
		message.Thread_id as 'ThreadId',
		datetime ((message.timestamp /10000000)-11644473600, 'unixepoch', 'localtime') as 'TimeStamp',
		message.Status as 'Status',
		case  
			message.Type 
				when 1 then 'Received' 
				when 2 then 'Sent' 
		end as 'Type',
		message.from_address as 'From Address',
		case 
			when message.from_address notnull
			then contact.display_name
		end as 'Sender',
		
		message.body as 'Body',
		conversation.summary as 'conversation summary',
		message_to_address.address as 'To Address',
		case 
			when message_to_address.address notnull
			then contact.display_name 
		end as 'Recipient',
		conversation.msg_count as 'mesgcount',
		case 
			when conversation.unread_count > 0
			then 'Yes'||', '||conversation.unread_count
			else 'No'
		end as 'unreadcount',
		message.pc_status
	    from message
		join conversation on message.thread_id = conversation.thread_id
		left join message_to_address on message.message_id = message_to_address.message_id
		left join address on address.address = message.from_address or address.address = message_to_address.address
		left join contact on contact.contact_id = address.contact_id
        group by message.message_id order by TimeStamp desc''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('YourPhone - Messages')
        report.start_artifact_report(report_folder, 'YourPhone - Messages')
        report.add_script()
        data_headers = ('MessageID', 'ThreadID', 'Timestamp', 'Status', 'Type', 'From Address', 'Sender', 'Body', 'Conversation Summary', 'To Address', 'Recipient', 'mesgcount', 'unreadcount', 'pc_status')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0],rows[1],rows[2],rows[3],rows[4],rows[5],rows[6],rows[7],rows[8],rows[9],rows[10],rows[11],rows[12],rows[13]))

        report.write_artifact_data_table(data_headers, data_list, phone_db)
        report.end_artifact_report()

        tsvname = f'YourPhone - Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_phone)
    else:
        logfunc('No phone.db Messages available')

    db.close()

    db = open_sqlite_db_readonly(photos_db)
    cursor = db.cursor()
    try:
        cursor.execute('''Select 
            photo_id,
            datetime(("last_updated_time"/ 10000000) - 11644473600, 'unixepoch') as 'LastUpdated',
            name,
            "size",
            uri
        from photo''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0

    if usageentries > 0:
        report = ArtifactHtmlReport('YourPhone - Photos')
        report.start_artifact_report(report_folder, 'YourPhone - Photos')
        report.add_script()
        data_headers = ('PhotoID', 'LastUpdated', 'Name', 'Size', 'Uri')
        
        data_list = []
        for rows in all_rows:
            data_list.append((rows[0], rows[1], rows[2], rows[3], rows[4]))

        report.write_artifact_data_table(data_headers, data_list, photos_db)
        report.end_artifact_report()

        tsvname = f'YourPhone - Photos'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_photos)
    else:
        logfunc('No Photos data available')

    db.close()
