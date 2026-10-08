"""
Capstone Group 8 - Invoice Processing System
Integrates business logic, OCR module, and frontend. Business logic controller.
Author: @slittle95
@sethzacharyroth-a11y contribution: Integrated PDF upload processing with OCR, validation,
and the human-in-the-loop invoice review workflow.
"""

import validation

import invoice_extraction.backend.parser_main as parser_main
from datetime import date
from dateutil.parser import parse

from schemas import (
    InvoiceCreate,
    InvoiceLineItemCreate,
)


def upload(target_path):
    """
    Process an uploaded invoice through OCR and validation.

    Validation errors do not stop the upload because imperfect OCR
    results are expected to be reviewed and corrected in the UI.
    str => tuple[InvoiceCreate, list[InvoiceLineItemCreate], list[list[float, float]]]
    """
    metadata, lineitems, confidences = use_ocr(target_path)
    val_result = validation.validate(metadata, lineitems)
    
    return metadata, lineitems, confidences, val_result


def use_ocr(filepath): 
    """
    Convert OCR/parser output into application schema objects.
    str => tuple[InvoiceCreate, list[InvoiceLineItemCreate], list[list[float, float]]]
    """
    payload = parser_main.receive_file(filepath)
    #parser returns JSON object containing Invoice and InvoiceLineItems

    if not isinstance(payload, dict):
        raise ValueError("OCR parser did not return the expected invoice data.")

    metadata = payload.get("Invoice", {})
    parsed_lineitems = payload.get("InvoiceLineItems", [])
    confidence_intervals = metadata.get("Confidence")
    if len(confidence_intervals) < 8:
        confidence_intervals = [0,0,0,0,0,0,0,0] #if one or more fields is missing we don't know which, so all confidence is 0

    invoice_number = metadata.get("InvoiceNumber", "")
    order_date = metadata.get("OrderDate")
    ship_date = metadata.get("ShipDate")
    due_date = metadata.get("DueDate")
    sales_no = metadata.get("SalesOrderNo", "")
    supplier = metadata.get("Supplier", "")

    if not invoice_number:
        invoice_number = 00000
        confidence_intervals[0] = 0
        #raise ValueError("OCR could not determine the invoice number.")
    if not supplier:
        confidence_intervals[1] = 0
    if not sales_no:
        confidence_intervals[3]
    
    if not order_date:
        order_date = date(1970,1,1)
        confidence_intervals[2] = 0
        #raise ValueError("OCR could not determine the order date.")
    else:
        order_date = parse(order_date).date()
    if not due_date:
        due_date = date(1970,1,1)
        confidence_intervals[4] = 0
        #raise ValueError("OCR could not determine the due date.")
    else:
        due_date = parse(due_date).date()    
    if not ship_date:
        ship_date = date(1970,1,1)
        confidence_intervals[5] = 0
        #raise ValueError("OCR could not determine the ship date.")
    else:
        ship_date = parse(ship_date).date()

    shipping_handling = metadata.get("ShippingHandling", 0)
    if shipping_handling is None or shipping_handling < 0:
        shipping_handling = 0.0
        confidence_intervals[6] = 0

    total_amt = metadata.get("TotalAmt", 0)
    if total_amt is None or total_amt < 0:
        total_amt = 0.0
        confidence_intervals[7] = 0

    invoice = InvoiceCreate(
        InvoiceNumber=invoice_number,
        OrderDate=order_date,
        ShipDate=ship_date,
        DueDate=due_date,
        SalesOrderNo=sales_no,
        ShippingHandling=float(shipping_handling),
        TotalAmt=float(total_amt),
        Supplier=supplier,
    )
    new_invoice_line_items = []

    for item in parsed_lineitems:
        rate = item.get("Rate")
        # A missing OCR value must still be numeric for the
        # application/database. Zero flags it for human review.
        if rate is None:
            rate = 0.0        
        
        amount = item.get("Amount")
        if amount is None:
            amount = 0.0        
        
        quantity = item.get("Quantity")
        if quantity is None or quantity < 0:
            if amount > 0 and rate > 0:
                quantity = amount / rate
            else:
                quantity = -1


        new_item = InvoiceLineItemCreate(
            InvoiceNumber=invoice_number,
            Quantity=int(quantity),
            SuppliersID=item.get("SuppliersID", ""),
            SuppliersDesc=item.get("Description", ""),
            Rate=float(rate),
            Amount=float(amount),
            LineCount=item.get("LineCount"),
        )
        new_invoice_line_items.append(new_item)

        confidence_intervals.append(float(item.get("Confidence", 0) or 0))

    return (
        invoice,
        new_invoice_line_items,
        confidence_intervals,

    )
def update(invoice, line_items):
    """
    Runs validation again when user edits.
    InvoiceCreate, list[InvoiceLineItemCreate] => str
    """
    result = validation.validate(invoice, line_items)
    return result 
