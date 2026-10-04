'''
Created on Sep 4, 2026

@author: Sally Little
'''
import validation
import inventory_updater
from inv import CompleteInvoice, InvoiceLine
import invoice_extraction.backend.parser_main as parser_main
from datetime import date
from dateutil.parser import parse
from schemas import (
    InvoiceCreate,
    InvoiceLineItemCreate,
    InvoiceLineItemUpdate,
    InvoiceUpdate,
)

def upload(target_path): # -> tuple[InvoiceCreate, list[InvoiceLineItemCreate], list[tuple[float, float]]]:
    metadata, lineitems, confidences, validatable_invoice = use_ocr(target_path)
    result = validation.validate(validatable_invoice)
    if result == "200":
        return metadata, lineitems, confidences
    else:
        pass #parse errors and pass all back to front end


def use_ocr(filepath):# -> tuple[InvoiceCreate, list[InvoiceLineItemCreate], list[tuple[float, float]], CompleteInvoice]:
    """
    This is the connector to the OCR module. It is the only function that is tightly coupled with the same.
    """
    payload = parser_main.receive_file(filepath)
    """
    receive_file returns structure of the shape:
    {
        "Invoice": 
            {
                "InvoiceNumber": str,
                "OrderDate": str,
                "ShipDate": str,
                "DueDate": str,
                "ShippingHandling": float, (negative if not supplied)
                "TotalAmt": float, (negative if not supplied)
                "Supplier": str,
            }
        "InvoiceLineItems": [{
                        "SuppliersID": str,
                        "Description": str,
                        "Quantity": int, (theoretically)
                        "HSCode": str,
                        "Rate": float,
                        "Amount": float,
                        "OCRConfidence": float,
                        "Confidence": float,
                        "LineCount": int,
                    }]
    }
    """
    
    metadata = payload.Invoice # pyright: ignore[reportOptionalMemberAccess,reportAttributeAccessIssue]
    InvoiceNumber=metadata.InvoiceNumber
    ShippingHandling=metadata.ShippingHandling
    TotalAmt=metadata.TotalAmt
    invoice = InvoiceCreate(
        InvoiceNumber=InvoiceNumber,
        OrderDate=parse(metadata.OrderDate).date(),
        ShipDate=parse(metadata.ShipDate).date(),
        DueDate=parse(metadata.DueDate).date(),
        SalesOrderNo=metadata.SalesOrderNo,
        ShippingHandling=ShippingHandling,
        TotalAmt=TotalAmt,
        Supplier=metadata.Supplier
    )
    validatable_invoice = CompleteInvoice(InvoiceNumber, ShippingHandling, TotalAmt)
    new_invoice_line_items = []
    confidence_intervals = []
    for item in payload.InvoiceLineItems: # pyright: ignore[reportOptionalMemberAccess,reportAttributeAccessIssue]
        new_item =InvoiceLineItemCreate(
            InvoiceNumber=metadata.InvoiceNumber,
            Quantity=int(item.Quantity),
            SuppliersID=item.SuppliersID,
            SuppliersDesc=item.Description,
            Rate= item.Rate,
            Amount=item.Amount,
            LineCount=item.LineCount,
        )
        new_validatable_item = InvoiceLine(item.Quantity, item.SuppliersID, item.SuppliersDesc, item.Rate, item.Amount)
        validatable_invoice.add_line_item(new_validatable_item)
        new_invoice_line_items.append(new_item)
        confidence_intervals.append((item.OCRConfidence, item.Confidence))
    return invoice, new_invoice_line_items, confidence_intervals, validatable_invoice



