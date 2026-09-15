from sqlalchemy.orm import Session
from models import Inventory, InvoiceLineItem, Invoice, Supplier
from schemas import (
    InventoryCreate,
    InventoryUpdate,
    InvoiceLineItemCreate,
    InvoiceLineItemUpdate,
    InvoiceCreate,
    InvoiceUpdate,
)


def get_all_inventory(db: Session):
    return db.query(Inventory).all()


def get_inventory_entry(db: Session, ProductID: str):
    return db.query(Inventory).filter(Inventory.ProductID == ProductID).first()


def create_inventory_entry(db: Session, passed_item: InventoryCreate):
    db_inventory = Inventory(**passed_item.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory_entry(db: Session, ProductID: str, passed_item: InventoryUpdate):
    db_inventory_entry = get_inventory_entry(db, ProductID)
    if not db_inventory_entry:
        return None
    for key, value in passed_item.model_dump().items():
        setattr(db_inventory_entry, key, value)
    db.commit()
    db.refresh(db_inventory_entry)
    return db_inventory_entry


def get_line_items(db: Session, InvoiceNumber: str):
    return db.query(InvoiceLineItem).filter(InvoiceLineItem.InvoiceNumber == InvoiceNumber).all()


def get_line_item(db: Session, InvoiceNumber: str, SuppliersID: str):
    return (
        db.query(InvoiceLineItem)
        .filter(
            InvoiceLineItem.InvoiceNumber == InvoiceNumber,
            InvoiceLineItem.SuppliersID == SuppliersID,
        )
        .first()
    )


def create_line_item(db: Session, passed_item: InvoiceLineItemCreate):
    db_line_item = InvoiceLineItem(**passed_item.model_dump())
    db.add(db_line_item)
    db.commit()
    db.refresh(db_line_item)
    return db_line_item


def update_line_item(db: Session, InvoiceNumber: str, SuppliersID: str, passed_line_item: InvoiceLineItemUpdate):
    db_line_item = get_line_item(db, InvoiceNumber, SuppliersID)
    if not db_line_item:
        return None
    for key, value in passed_line_item.model_dump().items():
        if key not in {"InvoiceNumber", "SuppliersID"}:
            setattr(db_line_item, key, value)
    db.commit()
    db.refresh(db_line_item)
    return db_line_item


def get_invoices(db: Session):
    return db.query(Invoice).all()


def get_invoice(db: Session, InvoiceNumber: str):
    return db.query(Invoice).filter(Invoice.InvoiceNumber == InvoiceNumber).first()


def create_invoice(db: Session, passed_item: InvoiceCreate):
    db_invoice = Invoice(**passed_item.model_dump())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def update_invoice(db: Session, InvoiceNumber: str, passed_item: InvoiceUpdate):
    db_invoice = get_invoice(db, InvoiceNumber)
    if not db_invoice:
        return None
    for key, value in passed_item.model_dump().items():
        setattr(db_invoice, key, value)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def get_suppliers(db: Session):
    return db.query(Supplier).all()


def get_supplier(db: Session, SupplierName: str):
    return db.query(Supplier).filter(Supplier.SupplierName == SupplierName).first()
