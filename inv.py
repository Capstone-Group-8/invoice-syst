'''
Created on Sep 4, 2026

@author: Sally Little
'''
class InvoiceLine():  
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

class CompleteInvoice():
    shipping: float
    total: float
    InvoiceNumber: str
    line_items: InvoiceLine[]
    
    def __init__(self, InvoiceNumber, shipping, total, line_items = []):
        self.shipping = shipping
        self.total = total
        self.InvoiceNumber = InvoiceNumber
        self.line_items = line_items

    def add_line_items(self, line_items):
        self.line_items = line_items

    def add_line_item(self, line_item):
        self.line_items.append(line_item)
        
    def print_invoice(self):
        print(self.InvoiceNumber, self.shipping, self.total)
