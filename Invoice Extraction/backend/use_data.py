'''
Created on Sep 4, 2026

@author: Sally Little
Just playing around with pushing the data to the main modules
'''

from inv import *
                

def parse_bullseye(lines, count):
    linecount = count
    supplier = "Bullseye Glass Co."
    current_count = count
    line = ""
    def parse_bullseye_line():
        lineitem = []
        if len(lines[current_count]) > 3:
            lineitem.append(1)
            lineitem.append(lines[current_count])
        else:
            lineitem.append(lines[current_count])
            lineitem.append(lines[current_count += 1])
        lineitem.append(lines[current_count += 1])
        lineitem.append(lines[current_count += 2])
        lineitem.append(lines[current_count += 1])
        while (len(lines[current_count += 1]) > 3):
            lineitem[len(lineitem)-4] += lines[current_count =+ 1]
        return lineitem
    while (line[:3] != "INV")
        if (line == "Purchase Order"):
            break
        current_count += 1
        line = lines[current_count]
    invoice_number = line
    while (line != "Order Date"):
        if (line == "Sales Rep" or line == "Shipping Terms"):
            break
        current_count += 1
        line = lines[current_count]
    current_count += 5
    order_date = lines[current_count]
    while (line != "Ship Date"):
        if (line == "Created From" or line == "Freight"):
            break
        current_count += 1
        line = lines[current_count]
    current_count += 4
    ship_date = lines[current_count]
    while (line != "Sales Order"):
        if (line == "Memo" or line == "Quantity"):
            break
        current_count += 1
        line = lines[current_count]
    current_count += 1
    sales_no = lines[current_count]
    line_items = []
    while (line !="Subtotal"): 
        while (line != "Amount"):
            current_count += 1
            line = lines[current_count]
        current_count += 1
        while (line[1:5] != " of "):
            new_line = parse_bullseye_line()
            line_items += InvoiceLine(new_line[0], new_line[1], new_line[2], new_line[3], new_line[4])
    shipping = lines[current_count +=5]
    while (line != "Total"):
        line = lines[current_count += 1]
    total = lines[current_count += 1]
    invoice = CompleteInvoice(invoice_number, shipping, total, line_items)
        
        

        
def parse(lines):
    suppliers = ["Bullseye Glass Co.", "Mountain Glass"]
    linecount = -1
    for i in lines:
        linecount += 1
        if i in suppliers:
            if i == "Bullseye Glass Co.":
                parse_bullseye(lines, linecount)    
    
        
