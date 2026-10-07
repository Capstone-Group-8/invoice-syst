'''
Unit test for testing the validation logic.
Author: Sally Little @slittle95
Aug 31 2026
'''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from datetime import date
import validation
from schemas import Invoice, InvoiceLineItem

invoice1 = Invoice(InvoiceNumber='INV009001', OrderDate=date(2025, 11, 5), ShipDate=date(2025, 12, 20),
                   DueDate =date(2026, 1, 15), SalesOrderNo='SO0005', ShippingHandling=617.42, TotalAmt=741.50, Supplier='Bullseye Glass Co.')
invoice2 = Invoice(InvoiceNumber='INV009001', OrderDate=date(2025, 11, 5), ShipDate=date(2025, 12, 20),
                   DueDate=date(2026, 1, 15), SalesOrderNo='SO0005', ShippingHandling=617.42, TotalAmt=855.93, Supplier='Bullseye Glass Co.')
invoice3 = Invoice(InvoiceNumber='INV009001', OrderDate=date(2025, 11, 5), ShipDate=date(2025, 12, 20),
                   DueDate=date(2026, 1, 15), SalesOrderNo='SO0005', ShippingHandling=617.42, TotalAmt=796.42, Supplier='Bullseye Glass Co.')
invoice4 = Invoice(InvoiceNumber='INV009001', OrderDate=date(2025, 11, 5), ShipDate=date(2025, 12, 20),
                   DueDate=date(2026, 1, 15), SalesOrderNo='SO0005', ShippingHandling=617.42, TotalAmt=3729.63, Supplier='Bullseye Glass Co.')


def test_syntax():
    my_invoice = invoice1
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000013-0001-F-P001', SuppliersDesc='Opaque White Opal Fine Frit 1lb jar', Rate=12.42, Amount=12.42, LineCount =1),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='00124-0030-F-FULL', SuppliersDesc='Red Full Double-Rolled', Rate=55.83, Amount=55.83, LineCount =2),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000025-030-F-FULL', SuppliersDesc='Tangerine Full Double-Rolled', Rate=55.83, Amount=55.83, LineCount =3),
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Syntax_error (line 2) /Syntax_error (line 3) /")

def test_semantic_1():
    my_invoice = invoice2
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000013-0001-F-P001', SuppliersDesc='Opaque White Opal Fine Frit 1 lb jar', Rate=12.42, Amount=12.42, LineCount =1), 
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1,SuppliersID= '000124-0030-F-FULL', SuppliersDesc='Red Full Double-Rolled', Rate=55.83, Amount=55.83, LineCount =2),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000025-0030-F-FULL', SuppliersDesc='Tangerine Full Double-Rolled', Rate=55.83, Amount=55.83, LineCount =3),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000104-0001-F-OZ05', SuppliersDesc='Glacier Blue Opalescent, Fine Frit', Rate=4.30, Amount=4.30, LineCount =4), #no 5 oz
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1,SuppliersID= '000113-0003-F-P005', SuppliersDesc='White Opalescent Frit, 5-lb jar', Rate=38.91, Amount=38.91, LineCount =5), #no 'coarse'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1,SuppliersID= '000126-0107-F-TUBE', SuppliersDesc='Spring Green Opalescent Stringer', Rate=15.39, Amount=15.39, LineCount =6), #no '1mm'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000100-0031-F-FULL', SuppliersDesc='Black Double-Rolled Iridescent Rainbow', Rate=55.83, Amount=55.83, LineCount =7)
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 4) /Semantic_error (line 5) /Semantic_error (line 6) /")


def test_semantic_2():
    my_invoice = invoice2
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000013-0001-F-P001', SuppliersDesc='Opaque White Opal Frit 1 lb jar', Rate=12.42, Amount=12.42, LineCount =1), #no 'fine'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000124-0030-F-FULL', SuppliersDesc='Red Full', Rate=55.83, Amount=55.83, LineCount =2), #no 'double-rolled'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000025-0030-F-FULL', SuppliersDesc='Tangerine Full Double-Rolled', Rate=55.83, Amount=55.83,LineCount =3),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000104-0001-F-OZ05', SuppliersDesc='Glacier Blue Opalescent, Fine Frit 5-oz jar', Rate=4.30, Amount=4.30, LineCount =4),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000113-0003-F-P005', SuppliersDesc='White Opalescent Coarse Frit, 5-lb jar', Rate=38.91, Amount=38.91, LineCount =5), 
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000126-0107-F-TUBE', SuppliersDesc='Spring Green Opalescent 1mm', Rate=15.39, Amount=15.39, LineCount =6), #no 'stringer'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000100-0031-F-FULL', SuppliersDesc='Black Double-Rolled Rainbow', Rate=55.83, Amount=55.83, LineCount =7) #no 'irid'
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 1) /Semantic_error (line 2) /Semantic_error (line 6) /Semantic_error (line 7) /")

def test_semantic_3():
    my_invoice = invoice2
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001116-0002-F-P001', SuppliersDesc='Opaque White Opal Frit 1lb jar', Rate=12.42, Amount=12.42, LineCount =1), #no 'med'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001116-0030-F-FULL', SuppliersDesc='Turquoise Blue Transparent Full', Rate=55.83, Amount=55.83, LineCount =2), #no 'double-rolled'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000025-0030-F-FULL', SuppliersDesc='Tangerine Full Double-Rolled', Rate=55.83, Amount=55.83, LineCount =3),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000104-0001-F-OZ05', SuppliersDesc='Glacier Blue Opalescent, Fine 5-oz jar', Rate=4.30, Amount=4.30, LineCount =4), # no 'frit'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000113-0003-F-P001', SuppliersDesc='White Opalescent Coarse Frit, 1-lb jar', Rate=38.91, Amount=38.91, LineCount =5), 
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000126-0272-F-TUBE', SuppliersDesc='Spring Green Opalescent 2mm Stringer', Rate=15.39, Amount=15.39, LineCount =6), 
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001101-0031-F-FULL', SuppliersDesc='Clear Trans Double-rolled Iridescent', Rate=55.83, Amount=55.83, LineCount =7) #no 'rainbow'
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 1) /Semantic_error (line 2) /Semantic_error (line 4) /Semantic_error (line 7) /")

def test_semantic_4():
    my_invoice = invoice2
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001116-0002-F-P001', SuppliersDesc='Opaque White Opal Medium Frit, 1lb jar', Rate=12.42, Amount=12.42, LineCount =1), 
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001116-0030-F-FULL', SuppliersDesc='Turquoise Blue Transparent Double-Rolled Full', Rate=55.83, Amount=55.83, LineCount =2), 
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000025-0030-F-FULL', SuppliersDesc='Tangerine Full', Rate=55.83, Amount=55.83, LineCount =3), #no double-rolled
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000104-0001-F-OZ05', SuppliersDesc='Glacier Blue Opalescent, Fine Frit 5-oz jar', Rate=4.30, Amount=4.30, LineCount =4),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000113-0003-F-P001', SuppliersDesc='White Opalescent Coarse Frit', Rate=38.91, Amount=38.91, LineCount =5), #no 1-lb
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000126-0272-F-TUBE', SuppliersDesc='Spring Green Opalescent stringer', Rate=15.39, Amount=15.39, LineCount =6), #no '2mm'
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001101-0031-F-FULL', SuppliersDesc='Clear Trans Double-rolled Iridescent rainbow', Rate=55.83, Amount=55.83, LineCount =7)
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 3) /Semantic_error (line 5) /Semantic_error (line 6) /")

def test_arithmetic():
    my_invoice = invoice3
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=2, SuppliersID='000013-0001-F-P001', SuppliersDesc='Opaque White Opal Fine Frit, 1lb jar', Rate=12.42, Amount=12.42, LineCount =1),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000024-0030-F-FULL', SuppliersDesc='Tomato Red Full double-rolled', Rate=55.38, Amount=55.83, LineCount =2),
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000025-0030-F-FULL', SuppliersDesc='Tangerine Full Double-Rolled', Rate=55.83, Amount=110.76, LineCount =3),
        ]
    test = validation.validate(my_invoice,my_line_items)
    assert(test == "Arithmetic_line_error (line 1) /Arithmetic_line_error (line 2) /Arithmetic_line_error (line 3) /Arithmetic_total_error /")

def test_multiples():
    my_invoice = invoice4
    my_line_items = [
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='13-01', SuppliersDesc='Opaque White Opal Fine Frit', Rate=12.42, Amount=22.42, LineCount =1), #syntax and arithmetic
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='000024-0030-F-FULL', SuppliersDesc='Tomato Red Full', Rate=55.38, Amount=55.83, LineCount =2), #semantic and arithmetic
        InvoiceLineItem(InvoiceNumber='INV009001',Quantity=1, SuppliersID='001116-0002-F-P001', SuppliersDesc='Opaque White Opal Frit', Rate=12.42, Amount=12.42, LineCount =3) #two semantic errors
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Syntax_error (line 1) /Arithmetic_line_error (line 1) /Semantic_error (line 2) /Arithmetic_line_error (line 2) /Semantic_error (line 3) /Semantic_error (line 3) /Arithmetic_total_error /")

 
if __name__ == "__main__":
    test_syntax()
    test_semantic_1()
    test_semantic_2()
    test_semantic_3()
    test_semantic_4()
    test_arithmetic()
    test_multiples()
    print("test complete")
