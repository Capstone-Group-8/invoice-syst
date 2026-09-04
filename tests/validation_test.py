'''
Unit test for testing the validation logic.
@Sally Little
Aug 31 2026
'''
import validation

class Invoice():
    shipping: float
    total: float
    InvoiceNumber: str
    
    def __init__(self, InvoiceNumber, shipping, total):
        self.shipping = shipping
        self.total = total
        self.InvoiceNumber = InvoiceNumber
        
    def print_invoice(self):
        print(self.InvoiceNumber, self.shipping, self.total)

class InvoiceLineItem():  
    Quantity: int
    SuppliersID: str
    Description: str
    Rate: float
    Amount: float
    
    def __init__(self, Quantity, SuppliersID, Description, Rate, Amount): 
        self.Quantity = Quantity
        self.SuppliersID = SuppliersID
        self.Description = Description
        self.Rate = Rate
        self.Amount = Amount
    
    def print_line_item(self):
        print(self.Quantity, self.SuppliersID, self. Description, self.Rate, self.Amount)


def test_syntax():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 741.50)
    my_line_items = [
        InvoiceLineItem(1, '000013-0001-F-P001', 'Opaque White Opal Fine Frit 1lb jar', 12.42, 12.42),
        InvoiceLineItem(1, '00124-0030-F-FULL', 'Red Full Double-Rolled', 55.83, 55.83),
        InvoiceLineItem(1, '000025-030-F-FULL', 'Tangerine Full Double-Rolled', 55.83, 55.83),
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Syntax_error (line 2) Syntax_error (line 3) ")

def test_semantic_1():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 855.93)
    my_line_items = [
        InvoiceLineItem(1, '000013-0001-F-P001', 'Opaque White Opal Fine Frit 1 lb jar', 12.42, 12.42), 
        InvoiceLineItem(1, '000124-0030-F-FULL', 'Red Full Double-Rolled', 55.83, 55.83),
        InvoiceLineItem(1, '000025-0030-F-FULL', 'Tangerine Full Double-Rolled', 55.83, 55.83),
        InvoiceLineItem(1, '000104-0001-F-OZ05', 'Glacier Blue Opalescent, Fine Frit', 4.30, 4.30), #no 5 oz
        InvoiceLineItem(1, '000113-0003-F-P005', 'White Opalescent Frit, 5-lb jar', 38.91, 38.91), #no 'coarse'
        InvoiceLineItem(1, '000126-0107-F-TUBE', 'Spring Green Opalescent Stringer', 15.39, 15.39), #no '1mm'
        InvoiceLineItem(1, '000100-0031-F-FULL', 'Black Double-Rolled Iridescent Rainbow', 55.83, 55.83)
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 4) Semantic_error (line 5) Semantic_error (line 6) ")


def test_semantic_2():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 855.93)
    my_line_items = [
        InvoiceLineItem(1, '000013-0001-F-P001', 'Opaque White Opal Frit 1 lb jar', 12.42, 12.42), #no 'fine'
        InvoiceLineItem(1, '000124-0030-F-FULL', 'Red Full', 55.83, 55.83), #no 'double-rolled'
        InvoiceLineItem(1, '000025-0030-F-FULL', 'Tangerine Full Double-Rolled', 55.83, 55.83),
        InvoiceLineItem(1, '000104-0001-F-OZ05', 'Glacier Blue Opalescent, Fine Frit 5-oz jar', 4.30, 4.30),
        InvoiceLineItem(1, '000113-0003-F-P005', 'White Opalescent Coarse Frit, 5-lb jar', 38.91, 38.91), 
        InvoiceLineItem(1, '000126-0107-F-TUBE', 'Spring Green Opalescent 1mm', 15.39, 15.39), #no 'stringer'
        InvoiceLineItem(1, '000100-0031-F-FULL', 'Black Double-Rolled Rainbow', 55.83, 55.83) #no 'irid'
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 1) Semantic_error (line 2) Semantic_error (line 6) Semantic_error (line 7) ")

def test_semantic_3():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 855.93)
    my_line_items = [
        InvoiceLineItem(1, '001116-0002-F-P001', 'Opaque White Opal Frit 1lb jar', 12.42, 12.42), #no 'med'
        InvoiceLineItem(1, '001116-0030-F-FULL', 'Turquoise Blue Transparent Full', 55.83, 55.83), #no 'double-rolled'
        InvoiceLineItem(1, '000025-0030-F-FULL', 'Tangerine Full Double-Rolled', 55.83, 55.83),
        InvoiceLineItem(1, '000104-0001-F-OZ05', 'Glacier Blue Opalescent, Fine 5-oz jar', 4.30, 4.30), # no 'frit'
        InvoiceLineItem(1, '000113-0003-F-P001', 'White Opalescent Coarse Frit, 1-lb jar', 38.91, 38.91), 
        InvoiceLineItem(1, '000126-0272-F-TUBE', 'Spring Green Opalescent 2mm Stringer', 15.39, 15.39), 
        InvoiceLineItem(1, '001101-0031-F-FULL', 'Clear Trans Double-rolled Iridescent', 55.83, 55.83) #no 'rainbow'
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 1) Semantic_error (line 2) Semantic_error (line 4) Semantic_error (line 7) ")

def test_semantic_4():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 855.93)
    my_line_items = [
        InvoiceLineItem(1, '001116-0002-F-P001', 'Opaque White Opal Medium Frit, 1lb jar', 12.42, 12.42), 
        InvoiceLineItem(1, '001116-0030-F-FULL', 'Turquoise Blue Transparent Double-Rolled Full', 55.83, 55.83), 
        InvoiceLineItem(1, '000025-0030-F-FULL', 'Tangerine Full', 55.83, 55.83), #no double-rolled
        InvoiceLineItem(1, '000104-0001-F-OZ05', 'Glacier Blue Opalescent, Fine Frit 5-oz jar', 4.30, 4.30),
        InvoiceLineItem(1, '000113-0003-F-P001', 'White Opalescent Coarse Frit', 38.91, 38.91), #no 1-lb
        InvoiceLineItem(1, '000126-0272-F-TUBE', 'Spring Green Opalescent stringer', 15.39, 15.39), #no '2mm'
        InvoiceLineItem(1, '001101-0031-F-FULL', 'Clear Trans Double-rolled Iridescent rainbow', 55.83, 55.83)
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Semantic_error (line 3) Semantic_error (line 5) Semantic_error (line 6) ")

def test_arithmetic():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 796.42)
    my_line_items = [
        InvoiceLineItem(2, '000013-0001-F-P001', 'Opaque White Opal Fine Frit, 1lb jar', 12.42, 12.42),
        InvoiceLineItem(1, '000024-0030-F-FULL', 'Tomato Red Full double-rolled', 55.38, 55.83),
        InvoiceLineItem(1, '000025-0030-F-FULL', 'Tangerine Full Double-Rolled', 55.83, 110.76),
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Arithmetic_line_error (line 1) Arithmetic_line_error (line 2) Arithmetic_line_error (line 3) Arithmetic_total_error ")

def test_multiples():
    InvoiceNumber = 'INV009001'
    my_invoice = Invoice(InvoiceNumber, 617.42, 3729.63)
    my_line_items = [
        InvoiceLineItem(1, '13-01', 'Opaque White Opal Fine Frit', 12.42, 22.42), #syntax and arithmetic
        InvoiceLineItem(1, '000024-0030-F-FULL', 'Tomato Red Full', 55.38, 55.83), #semantic and arithmetic
        InvoiceLineItem(1, '001116-0002-F-P001', 'Opaque White Opal Frit', 12.42, 12.42) #two semantic errors
        ]
    test = validation.validate(my_invoice, my_line_items)
    assert(test == "Syntax_error (line 1) Arithmetic_line_error (line 1) Semantic_error (line 2) Arithmetic_line_error (line 2) Semantic_error (line 3) Semantic_error (line 3) Arithmetic_total_error ")

 
