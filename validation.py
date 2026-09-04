'''
Created on Aug 26, 2026

@author: Sally Little
'''
#from fastapi import Depends
#from main import get_db
#from models import Invoice, InvoiceLineItem
#import crud
import re


#invoice = crud.get_invoice(Depends(get_db), InvoiceNumber)
#line_items = crud.get_line_items(Depends(get_db), InvoiceNumber)

def fail_line_semantic_validation(key, desc, count):
    #rewrite this function to present the error to the user
    #and guess the correction?
    print(f"Failed line validation: {desc}\nSupplier ID implies {key}, but the description does not contain the keyword(s).")
    #return(f"Semantic_error (line {count}) ")

def fail_line_syntactic_validation(SupplierID, count):
    #rewrite this function to present the error to the user
    print(f"Failed line validation: {SupplierID} does not follow the required format.")
    return(f"Syntax_error (line {count}) ")

def fail_line_arithmetic_validation(line, count):
    #rewrite this function to present the error to the user
    #and guess the correction?
    print(f"Failed line validation: {line.SuppliersID}\n{line.Quantity} times ${line.Rate} is not ${line.Amount}")
    return(f"Arithmetic_line_error (line {count}) ")

def fail_total_arithmetic_validation(invoice, subtotal):
    #rewrite this function to present the error to the user
    #and guess the correction?
    print(f"Failed total validation:\nSubtotal ${subtotal} + shipping cost ${invoice.shipping} is not ${invoice.total}")
    return(f"Arithmetic_total_error ")


def test_line_semantic_validation(line, group1, group3, count):
    def check_desc_for(keys):
        desc = line.Description.lower()
        print("desc", desc)
        for key in keys:
            print("key", key)
            if key not in desc:
                print("fail")
                fail_line_semantic_validation(keys, line.Description, count)
                return(f"Semantic_error (line {count}) ")
        print("pass")
        return "200"
    return_group = ""
    if (group1 == '0030'):
        return_group += check_desc_for(['double-rolled'])
    elif (group1 == '0031'):
        return_group += check_desc_for(['double-rolled', 'irid', 'rainbow'])
    elif (group1 == '0001'):
        return_group += check_desc_for(['fine', 'frit'])
    elif (group1 == '0002'):
        return_group += check_desc_for(['med','frit'])
    elif (group1 == '0003'):
        return_group += check_desc_for(['coarse', 'frit'])
    elif (group1 == '0008'):
        return_group += check_desc_for(['powder'])
    elif (group1 == '0107'):
        print("in the 1mm stringer case")
        return_group += check_desc_for(['stringer','1','mm'])
    elif (group1 == '0272'):
        return_group += check_desc_for(['stringer','2','mm'])
    if (group3 == 'P001'):
        return_group += check_desc_for(['1','lb'])
    elif (group3 == 'P005'):
        return_group += check_desc_for(['5','lb'])
    elif (group3 == 'OZ05'):
        return_group += check_desc_for(['5', 'oz'])
    x = re.search("error", return_group)
    #print("return_group = ",return_group)
    if x:
        returnable = return_group.replace('200','')
        #print("returnable = ", returnable)
        return returnable
    else:
        return '200'

def validate(invoice, line_items):
    subtotal = 0
    errors = ""
    count = 0
    for i in line_items:
        count += 1
        #test the regex
        x = re.search(r"0[0-9]{5}-[0-9]{4}-[A-Z]-[A-Z0-9]{4}", i.SuppliersID)
        if not x:
            errors += fail_line_syntactic_validation(i.SuppliersID, count)
        else:
            id = x.group()
            #print(x)
            #print(id)
            group1 = id[7:11]
            group3 = id[-4:]
            #print(group3, group1)
            semantic_result = test_line_semantic_validation(i, group1, group3, count)
            if (semantic_result != '200'):
                errors += semantic_result
        if (i.Quantity * i.Rate != i.Amount):
            errors += fail_line_arithmetic_validation(i, count)
        subtotal += i.Amount
    if (subtotal + invoice.shipping != invoice.total):
        errors += fail_total_arithmetic_validation(invoice, subtotal)
    if (errors == ""):
        return "200"
    else:
        return errors
               
        
        
