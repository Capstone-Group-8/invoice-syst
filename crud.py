from sqlalchemy.orm import Session
from models import Inventory, InvoiceLineItem, Invoice, Supplier
from schemas import InventoryCreate, InventoryUpdate, InvoiceLineItemCreate, InvoiceLineItemUpdate, InvoiceCreate, InvoiceUpdate

def get_all_inventory(db: Session):
    return db.query(Inventory).all()

def get_inventory_entry(db: Session, ProductID: str):
    return db.query(Inventory).filter(Inventory.ProductID == ProductID).first()

def create_inventory_entry(db: Session, passed_item: InventoryCreate):
    db_inventory = Inventory(
        ProductID=passed_item.ProductID,
        SuppliersID=passed_item.SuppliersID,
        Description=passed_item.Description,
        ProductType=passed_item.ProductType,
        QtyOnHand=passed_item.QtyOnHand,
        LastPrice=passed_item.LastPrice,
        TotalQtyDesired=passed_item.TotalQtyDesired,
        Supplier=passed_item.Supplier
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def update_inventory_entry(db: Session, ProductID: int, passed_item: InventoryUpdate):
    db_inventory_entry = get_inventory_entry(db, ProductID)
    if ProductID:
        db_inventory_entry.SuppliersID = passed_item.riskName
        db_inventory_entry.Description = passed_item.Description
        db_inventory_entry.ProductType = passed_item.ProductType
        db_inventory_entry.QtyOnHand = passed_item.QtyOnHand
        db_inventory_entry.LastPrice = passed_item.LastPrice
        db_inventory_entry.TotalQtyDesired = passed_item.TotalQtyDesired
        db_inventory_entry.Supplier=passed_item.Supplier
        db.commit()
        db.refresh(db_inventory_entry)
    return db_inventory_entry

'''def delete_inventory_entry(db: Session, ProductID: str):
    db_inventory = get_inventory_entry(db, ProductID)
    if db_inventory:
        db.delete(db_inventory)
        db.commit()
    return db_inventory'''


###################issues
#def get_line(db: Session):
 #   return db.query(InvoiceLineItem).all()

def get_line_items(db: Session, InvoiceNumber: str):
    return db.query(InvoiceLineItem).filter(InvoiceLineItem.InvoiceNumber == InvoiceNumber)

def get_line_item(db: Session, InvoiceNumber: str, SuppliersID: str):
    return db.query(InvoiceLineItem).filter(InvoiceLineItem.InvoiceNumber == InvoiceNumber and InvoiceLineItem.SuppliersID == SuppliersID).first()

def create_line_item(db: Session, passed_item: InvoiceLineItemCreate):
    db_line_item = InvoiceLineItem(
        InvoiceNumber=passed_item.InvoiceNumber,
        Quantity=passed_item.quantity,
        SuppliersID = passed_item.SuppliersID,
        Rate=passed_item.Rate,
        Amount=passed_item.Amount
    )
    db.add(db_line_item)
    db.commit()
    db.refresh(db_line_item)
    return db_line_item

def update_line_item(db: Session, InvoiceNumber: str, SuppliersID: str, passed_line_item: InvoiceLineItemUpdate):
    db_line_item = get_line_item(db, InvoiceNumber, SuppliersID)
    if InvoiceNumber and SuppliersID:
        db_line_item.Quantity = passed_line_item.Quantity
        db_line_item.SuppliersDesc = passed_line_item.SuppliersDesc
        db_line_item.Rate = passed_line_item.Rate
        db_line_item.Amount = passed_line_item.Amount
        db.commit()
        db.refresh(db_line_item)
    return db_line_item

'''def delete_line_item(db: Session, InvoiceNumber: str, SuppliersID: str):
    db_line_item = get_line_item(db, InvoiceNumber, SuppliersID)
    if db_line_item:
        db.delete(db_line_item)
        db.commit()
    return db_line_item'''



##################
def get_invoices(db: Session):
    return db.query(Invoice).all()

def get_invoice(db: Session, InvoiceNumber: int):
    return db.query(Invoice).filter(Invoice.InvoiceNumber == InvoiceNumber).first()

def create_invoice(db: Session, passed_item: InvoiceCreate):
    db_invoice = Invoice(
        InvoiceNumber=passed_item.InvoiceNumber,
        OrderDate=passed_item.OrderDate,
        ShipDate=passed_item.ShipDate,
        DueDate=passed_item.DueDate,
        ShippingHandling=passed_item.ShippingHandling,
        TotalAmt=passed_item.TotalAmt,
        Supplier=passed_item.Supplier
        #, File=passed_item.File
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def update_invoice(db: Session, InvoiceNumber: str, passed_item: InvoiceUpdate):
    db_invoice = get_invoice(db, InvoiceNumber)
    if InvoiceNumber:
        db_invoice.OrderDate = passed_item.OrderDate
        db_invoice.ShipDate = passed_item.ShipDate
        db_invoice.DueDate = passed_item.DueDate
        db_invoice.SalesOrderNo = passed_item.SalesOrderNo
        db_invoice.ShippingHandling = passed_item.ShippingHandling
        db_invoice.TotalAmt = passed_item.TotalAmt
        db_invoice.Supplier = passed_item.Supplier
        db.commit()
        db.refresh(db_invoice)
    return db_invoice

'''def delete_invoice(db: Session, InvoiceNumber: str):
    db_invoice = get_invoice(db, InvoiceNumber)
    if db_invoice:
        db.delete(db_invoice)
        db.commit()
    return db_invoice'''

################################

def get_suppliers(db: Session):
    return db.query(Supplier).all()

def get_supplier(db: Session, SupplierName: str):
    return db.query(Invoice).filter(Supplier.SupplierName == SupplierName).first()

#I see no reason to have these but have left stub code in case I'm overlooking

# def create_supplier(db: Session, passed_item: SupplierCreate):
#     db_supplier = Supplier(
#
#
#     )
#     db.add(db_supplier)
#     db.commit()
#     db.refresh(db_supplier)
#     return db_supplier
#
# def update_supplier(db: Session, SupplierName: str, passed_item: SupplierUpdate):
#     db_supplier = get_supplier(db, SupplierName)
#     if SupplierName:
#
#         db.commit()
#         db.refresh(db_supplier)
#     return db_supplier


