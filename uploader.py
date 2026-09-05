'''
Created on Sep 4, 2026

@author: Sally Little
'''
import validation
import inventory_updater
from inv import CompleteInvoice

def use_ocr(payload):
    

def push_initial_read(payload):
    payload, scores = calls the ocr
    creates new invoice called invoice using the payload.
   calls (/invoices/all POST which calls) main.create_new_invoice once
    calls (/invoices/{InvoiceNumber/lineitems POST which calls) main.create_new_line_item repeatedly with payload
    scores = validation.update_confidence_scores(invoice, scores)
    editInvoice(invoice.InvoiceNumber, order_date, ship_date, due_date, sales_no, invoice.shipping, invoice.total, supplier)
    
def push_updated_read():
    calls (/invoices/{InvoiceNumber} which calls) main.update_invoice, which calls crud.update_invoice,
    calls main.update_line_item REPEATEDLY FOR ALL UPDATED LINE ITEMS. 
    inventory_updater.update(payload)
