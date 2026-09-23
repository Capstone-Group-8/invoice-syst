import os
import sys
import aiofiles

from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session 
from pathlib import Path

import crud
import models

from invoice_extraction.backend.parser_main import process_file, DROPBOX
import uploader
import inventory_updater
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
    allow_origins= origins,
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
    #print(f"Fetching invoice using: {InvoiceNumber} calling crud.get_invoice from line 84 of main.py")
    invoice = crud.get_invoice(db, InvoiceNumber)
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    return invoice


@app.get("/invoices/{InvoiceNumber}/lineitems", response_model=list[InvoiceLineItem])
def read_invoice_items(InvoiceNumber: str, db: Session = Depends(get_db)):
    return crud.get_line_items(db, InvoiceNumber)

@app.get("/inventory/{ProductID}", response_model=Inventory)
def read_inventory_entry(ProductID: str, db: Session = Depends(get_db)):
    inventory_entry = crud.get_inventory_entry(db, ProductID)
    if not inventory_entry:
        raise HTTPException(status_code=404, detail="inventory entry not found")
    return inventory_entry

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




@app.put("/invoices/{InvoiceNumber}", response_model=Invoice)
def update_invoice(InvoiceNumber: str, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    #print(f"Updating invoice with InvoiceNumber: {InvoiceNumber} by calling crud.update_invoice from line 122 of main.py\n{invoice}")  # Debugging statement
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

def cache_inventory(db: Session = Depends(get_db)):
    inventory = read_inventory(db)
    d = dict()
    product_ids = [0]
    for item in inventory:
        d[item.SuppliersID] = item
        product_ids.append(int(item.ProductID))
    return d, max(product_ids)

@app.put("/fake/endpoint/for/testing")
def handle_invoice(metadata, lineitems, confidence_intervals, db: Session = Depends(get_db), test_toggle=False):
    create_new_invoice(metadata, db)
    for item in lineitems:
        create_new_line_item(metadata.InvoiceNumber, item, db)
    #cause react to open the form updater
    #pass forward the confidence intervals
    #retrieve the changes
    #update_invoice
    #update line_items
    if test_toggle:
        new_lineitems = lineitems #to enable testing to still work without actual updates
    inventory, current_max = cache_inventory(db)
    updated_items, new_items = inventory_updater.update(inventory, current_max, new_lineitems, metadata.Supplier)
    for productID, item in updated_items:
        update_inventory(productID, item, db)
    for item in new_items:
        create_new_inventory_entry(item, db)


@app.post("/upload")
#https://medium.com/@ThinkingLoop/fastapi-file-uploads-clean-fast-and-foolproof-4ecf0f00404f
async def upload_file(file: UploadFile):
    name = file.filename
    target = os.path.join(DROPBOX,name) # pyright: ignore[reportCallIssue, reportArgumentType]
    if file.content_type not in {"application/pdf"}:
        raise HTTPException(415, "Unsupported file type")
    else:
        async with aiofiles.open(target, "wb") as out:
            while chunk := await file.read(1024 * 1024):
                await out.write(chunk)
        #return {"stored_as": str(target)}
    metadata, lineitems, confidence_intervals = uploader.use_ocr(target)
    return handle_invoice(metadata, lineitems, confidence_intervals)    
    