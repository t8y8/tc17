####
# This script demonstrates how to use the Tableau Server Client
# to publish a workbook to a Tableau server. It will publish
# a specified workbook to the 'default' project of the given server.
#
# Note: The REST API publish process cannot automatically include
# extracts or other resources that the workbook uses. Therefore,
# a .twb file with data from a local computer cannot be published,
# unless packaged into a .twbx file.
#
# For more information, refer to the documentations on 'Publish Workbook'
# (https://onlinehelp.tableau.com/current/api/rest_api/en-us/help.htm)
#
# To run the script, you must have installed Python 2.7.X or 3.3 and later.
####

import argparse
import getpass
import logging

# pip install tableauserverclient
import tableauserverclient as TSC

def main():
    ##### Code to set up command line arguments
    parser = argparse.ArgumentParser(description='Publish a workbook to server.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--filepath', '-f', required=True, help='filepath to the workbook to publish')
    parser.add_argument('--site', '-i', help='id of site to sign into')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    args = parser.parse_args()
    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)
    ##### End set up


    # Step 1: Sign in to server.
    tableau_auth = TSC.TableauAuth(args.username, password, site_id=args.site)
    server = TSC.Server(args.server)
    server.use_server_version()

    with server.auth.sign_in(tableau_auth):
        # Step 2: Get projects on the site, then look for the default one.
        all_projects, pagination_item = server.projects.get()
        default_project = next((project for project in all_projects if project.is_default()), None)

        # Step 3: If default project is found, continue with publishing.
        if default_project is not None:
            # Define publish mode, create new workbook, publish
            overwrite_true = TSC.Server.PublishMode.Overwrite
            new_workbook = TSC.WorkbookItem(default_project.id)
            new_workbook = server.workbooks.publish(new_workbook, args.filepath, overwrite_true)
            print("Workbook published. ID: {0}".format(new_workbook.id))
        else:
            error = "The default project could not be found."
            raise LookupError(error)

if __name__ == '__main__':
    main()
