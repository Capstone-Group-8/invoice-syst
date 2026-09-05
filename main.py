from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session # in session.py

from database import SessionLocal, engine
import models
import crud
from schemas import Inventory, InventoryCreate, InventoryUpdate, Invoice, InvoiceCreate, InvoiceUpdate, InvoiceLineItem, InvoiceLineItemUpdate, InvoiceLineItemCreate, Supplier

## add the following to solve CORE problem
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
## add the following to satisfy CORE
app.add_middleware(
    CORSMiddleware,
    #allow_origins=["*"],  # or ["http://localhost:8000"] for security
    allow_origins=["http://localhost:8000"],  # for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency: DB session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# RESTful CRUD Endpoints
# -------------------------

@app.get("/invoices/all", response_model=list[Invoice])
def read_invoices(db: Session = Depends(get_db)):
    return crud.get_invoices(db)

@app.get("/inventory", response_model=list[Inventory])
def read_inventory(db: Session = Depends(get_db)):
    return crud.get_all_inventory(db)

@app.get("/suppliers", response_model=list[Supplier])
def read_suppliers(db: Session = Depends(get_db)):
    return crud.get_suppliers(db)
#no use case to read list of line items outside invoice context

@app.get("/invoices/{InvoiceNumber}", response_model=Invoice)
def read_invoice(InvoiceNumber: str, db: Session = Depends(get_db)):
    invoice = crud.get_invoice(db, InvoiceNumber)
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    return invoice

@app.get("/invoices/{InvoiceNumber}/lineitems", response_model=list[InvoiceLineItem])
def read_invoice_items(InvoiceNumber: str, db: Session = Depends(get_db)):
    line_items = crud.get_line_items(db, InvoiceNumber)
    return line_items
#need a function to read one line item/inventory entry?
#no use case to read one supplier


@app.post("/invoices/all", response_model=Invoice)
def create_new_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    return crud.create_invoice(db, invoice)

#is this also an http endpoint?
def create_new_line_item(line_item: InvoiceLineItemCreate, db: Session = Depends(get_db)):
    return crud.create_line_item(db, line_item)

@app.post("/inventory", response_model=Inventory)
def create_new_inventory_entry(entry: InventoryCreate, db: Session = Depends(get_db)):
    return crud.create_inventory_entry(db, entry)
#no use case to create new supplier


@app.put("/invoices/{InvoiceNumber}", response_model=Invoice)
def update_invoice(InvoiceNumber: str, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    updated = crud.update_invoice(db, InvoiceNumber, invoice)
    if not updated:
        raise HTTPException(status_code=404, detail="invoice not found")
    return updated

@app.put("/lineitem/{InvoiceNumber}", response_model=InvoiceLineItem) #are you sure about that URL
def update_line_item(InvoiceNumber: str, SuppliersID: str, line_item: InvoiceLineItemUpdate, db: Session = Depends(get_db)):
    updated = crud.update_line_item(db, InvoiceNumber, SuppliersID, line_item)
    if not updated:
        raise HTTPException(status_code=404, detail="line item not found")
    return updated

@app.put("/inventory/{ProductID}", response_model=Inventory)
def update_inventory(ProductID: str, inventory_entry: InventoryUpdate, db: Session = Depends(get_db)):
    updated = crud.update_inventory_entry(db, ProductID, inventory_entry)
    if not updated:
        raise HTTPException(status_code=404, detail="Inventory entry not found")
    return updated
#no use case to update supplier

# @app.delete("/{item_type}/{ID}")
# def delete_existing_item(ID: int, item_type: str, db: Session = Depends(get_db)):
#     deleted = crud.delete_item(db, ID, item_type)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="item not found")
#     return {"message": "item deleted"}

