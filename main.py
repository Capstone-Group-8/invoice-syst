import os
import sys

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import models

sys.path.insert(1, 'Invoice Extraction/backend')
from parser_main import process_file
from database import SessionLocal, engine
from schemas import (
    Inventory,
    InventoryCreate,
    InventoryUpdate,
    Invoice,
    InvoiceCreate,
    InvoiceLineItem,
    InvoiceLineItemCreate,
    InvoiceLineItemUpdate,
    InvoiceUpdate,
    Supplier,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Invoice Processing System API", version="0.1.0-alpha")

origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins="*", #leave until I can get past the access-control-allow-origin error
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/invoices/all", response_model=list[Invoice])
def read_invoices(db: Session = Depends(get_db)):
    return crud.get_invoices(db)


@app.get("/inventory", response_model=list[Inventory])
def read_inventory(db: Session = Depends(get_db)):
    return crud.get_all_inventory(db)


@app.get("/suppliers", response_model=list[Supplier])
def read_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)


@app.get("/invoices/{InvoiceNumber}", response_model=Invoice)
def read_invoice(InvoiceNumber: str, db: Session = Depends(get_db)):
    invoice = crud.get_invoice(db, InvoiceNumber)
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    return invoice


@app.get("/invoices/{InvoiceNumber}/lineitems", response_model=list[InvoiceLineItem])
def read_invoice_items(InvoiceNumber: str, db: Session = Depends(get_db)):
    return crud.get_line_items(db, InvoiceNumber)


@app.post("/invoices/all", response_model=Invoice, status_code=201)
def create_new_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    return crud.create_invoice(db, invoice)


@app.post("/invoices/{InvoiceNumber}/lineitems", response_model=InvoiceLineItem, status_code=201)
def create_new_line_item(InvoiceNumber: str, line_item: InvoiceLineItemCreate, db: Session = Depends(get_db)):
    if line_item.InvoiceNumber != InvoiceNumber:
        raise HTTPException(status_code=400, detail="Invoice number does not match request path")
    return crud.create_line_item(db, line_item)


@app.post("/inventory", response_model=Inventory, status_code=201)
def create_new_inventory_entry(entry: InventoryCreate, db: Session = Depends(get_db)):
    return crud.create_inventory_entry(db, entry)

@app.post("/upload")
def upload_file(file):
    return process_file(file)

@app.put("/invoices/{InvoiceNumber}", response_model=Invoice)
def update_invoice(InvoiceNumber: str, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    updated = crud.update_invoice(db, InvoiceNumber, invoice)
    if not updated:
        raise HTTPException(status_code=404, detail="invoice not found")
    return updated


@app.put("/lineitems/{InvoiceNumber}/{SuppliersID}", response_model=InvoiceLineItem)
def update_line_item(
    InvoiceNumber: str,
    SuppliersID: str,
    line_item: InvoiceLineItemUpdate,
    db: Session = Depends(get_db),
):
    updated = crud.update_line_item(db, InvoiceNumber, SuppliersID, line_item)
    if not updated:
        raise HTTPException(status_code=404, detail="line item not found")
    return updated


@app.put("/inventory/{ProductID}", response_model=Inventory)
def update_inventory(ProductID: str, inventory_entry: InventoryUpdate, db: Session = Depends(get_db)):
    updated = crud.update_inventory_entry(db, ProductID, inventory_entry)
    if not updated:
        raise HTTPException(status_code=404, detail="inventory entry not found")
    return updated
