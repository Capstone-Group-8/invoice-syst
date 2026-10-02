from datetime import date, time
from pydantic import BaseModel


class InventoryBase(BaseModel):
    SuppliersID: str | None = None
    Description: str
    ProductType: str
    QtyOnHand: int
    LastPrice: float | None = None
    TotalQtyDesired: int | None = None
    Supplier: str | None = None


class InventoryCreate(InventoryBase):
    ProductID: str


class InventoryUpdate(InventoryBase):
    pass


class Inventory(InventoryBase):
    ProductID: str
    model_config = {"from_attributes": True}


class InvoiceLineItemBase(BaseModel):
    InvoiceNumber: str
    Quantity: int
    SuppliersID: str
    SuppliersDesc: str
    Rate: float
    Amount: float

class InvoiceLineItemCreate(InvoiceLineItemBase):
    pass

class InvoiceLineItemUpdate(InvoiceLineItemBase):
    pass

class InvoiceLineItem(InvoiceLineItemBase):
    model_config = {"from_attributes": True}


class InvoiceBase(BaseModel):
    OrderDate: date
    ShipDate: date 
    DueDate: date
    SalesOrderNo: str 
    ShippingHandling: float 
    TotalAmt: float 
    Supplier: str 

class InvoiceCreate(InvoiceBase):
    InvoiceNumber: str

class InvoiceUpdate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    InvoiceNumber: str
    model_config = {"from_attributes": True}



class SupplierBase(BaseModel):
    ContactName: str | None = None
    ContactEmail: str | None = None
    ContactPhone: str | None = None


class Supplier(SupplierBase):
    SupplierName: str
    model_config = {"from_attributes": True}



class ChangeLogBase(BaseModel):
    InvoiceID: str
    FieldChanged: str
    OldValue: str
    NewValue: str
    Author: str | None = None
    Timestamp: time | None = None

class ChangeLogCreate(ChangeLogBase):
    pass

class ChangeLog(ChangeLogBase):
    ChangeID: int
    model_config = {"from_attributes": True}