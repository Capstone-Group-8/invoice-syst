'''
Created on Sep 4, 2026

@author: Sally Little
'''
def update():
    calls GET /invoices/{InvoiceNumber/lineitems, which calls main.read_invoice_items, which calls crud.get_line_items OR MAYBE IT GETS THEM STRAIGHT FROM uploader.PY?

    all_supplierIDs = obtain complete list of supplierIDs from inventory (GET /inventory/all and trim)

    for i in payload:
        if (i.supplierID in all_supplierIDs):
            updates the 'have' number: calls (/inventory/{ProductID} PUT which calls) main.update_inventory, which calls crud.update_inventory_entry.
        else:
            calls (/inventory POST which calls) main.create_new_inventory_entry, which calls crud.create_inventory_entry.


