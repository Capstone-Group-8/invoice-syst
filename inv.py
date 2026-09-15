'''Simple invoice objects used by the validation module.'''


class InvoiceLine:
    def __init__(self, Quantity, SuppliersID, Description, Rate, Amount):
        self.Quantity = Quantity
        self.SuppliersID = SuppliersID
        self.Description = Description
        self.Rate = Rate
        self.Amount = Amount

    def print_line_item(self):
        print(self.Quantity, self.SuppliersID, self.Description, self.Rate, self.Amount)


class CompleteInvoice:
    def __init__(self, InvoiceNumber, shipping, total, line_items=None):
        self.shipping = shipping
        self.total = total
        self.InvoiceNumber = InvoiceNumber
        self.line_items = list(line_items) if line_items is not None else []

    def add_line_items(self, line_items):
        self.line_items = list(line_items)

    def add_line_item(self, line_item):
        self.line_items.append(line_item)

    def print_invoice(self):
        print(self.InvoiceNumber, self.shipping, self.total)
