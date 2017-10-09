import os
import getpass
import pprint
import tempfile
from collections import defaultdict

import tableauserverclient as TSC
from tableaudocumentapi import Workbook

DB_SERVER = 'mssql.test.tsi.lan'

def get_workbook_info(wbds):
    #  Make a temp file for downloading the workbook
    temp = tempfile.NamedTemporaryFile(delete=False)
    try:
        #  Downlaod the workbook into a temp file, without the extract
        server.workbooks.download(wb.id, temp.name, include_extract=False)
        #  Open the workbook in the doc api and pull the info we need
        parsed = Workbook(temp.name)
        return parsed
    except Exception as e:
        print(e)
    finally:
        temp.close()
        os.remove(temp.name)


#  Setting up sign in for Tableau Online
password = getpass.getpass()
authz = TSC.TableauAuth('tdoyle@tableau.com', password, site_id='dinosaursinc')

#  Sign TSC into Tableau Online
server = TSC.Server("https://10ax.online.tableau.com")
server.use_server_version()
server.auth.sign_in(authz)

#  This will hold the workbook names and fields in use.
#  This could be a database or something else that stores this more permanently
USED_IN = defaultdict(list)

#  The fun part! Loop over all workbooks on Server download them
#  grab their data sources and loop through those. If any of the data sources
#  connections point to the server I'm interested in, pull those fields out
#  and stick them into the USED_IN dictionary.
for wb in TSC.Pager(server.workbooks):
    workbook_info = get_workbook_info(wb)

    #  Get data sources for the workbook
    datasources = workbook_info.datasources

    # Loop over the data sources and get connections
    for ds in datasources:
        connections = ds.connections

        #  If it doesn't connect to the database we care about, ingore it.
        if not any(conn.server == DB_SERVER for conn in connections):
            continue
        
        #  For each field , check if it's in use.
        for f in ds.fields.values():
            if f.worksheets:
                USED_IN[wb.name].append((f.name, f.calculation))


#  Print out the results
pprint.pprint(USED_IN)