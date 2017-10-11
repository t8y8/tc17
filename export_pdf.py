import getpass
import os
import tableauserverclient as TSC

password = getpass.getpass("Password: ")

auth = TSC.TableauAuth("cshin@tableau.com", password, site_id="dinosaursinc")
server = TSC.Server("https://10ax.online.tableau.com")
server.use_server_version()

# Custom fields
tag_to_filter = "report"
new_folder_path = "Report/"

with server.auth.sign_in(auth):
    # Specify a filter to only get workbooks tagged with 'report' tag
    tag_filter = TSC.RequestOptions()
    tag_filter.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags,
                                  TSC.RequestOptions.Operator.Equals,
                                  tag_to_filter))

    # Loop through filtered workbooks
    for workbook in TSC.Pager(server.workbooks, tag_filter):
        # Create a new directory for each workbook
        workbook_path = new_folder_path + workbook.name
        os.makedirs(workbook_path)

        # Get all views for workbook
        server.workbooks.populate_views(workbook)

        # Loop through all views of a workbook
        for view in workbook.views:
            # Get the PDF file from server
            server.views.populate_pdf(view)

            # Save PDF file locally
            file_path = workbook_path + "/" + view.name + ".pdf"
            with open(file_path, "w") as image_file:
                image_file.write(view.pdf)

            print("\tPDF of {0} downloaded from {1} workbook".format(view.name, workbook.name))

""" 
Specifying PDF format (optional)
    size = TSC.PDFRequestOptions.PageType.A4
    orientation = TSC.PDFRequestOptions.Orientation.Landscape
    req_option = TSC.PDFRequestOptions(size, orientation)
    server.views.populate_pdf(view, req_option)
"""
