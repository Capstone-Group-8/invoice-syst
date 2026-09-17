from datetime import date
from pydantic import BaseModel


class InventoryBase(BaseModel):
    SuppliersID: str
    Description: str
    ProductType: str
    QtyOnHand: int
    LastPrice: float
    TotalQtyDesired: int
    Supplier: str


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
