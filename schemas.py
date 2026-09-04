from pydantic import BaseModel
from datetime import date

class InventoryBase(BaseModel):
    SuppliersID: str
    Description: str
    ProductType: str
    QtyOnHand: int
    LastPrice: float
    TotalQtyDesired: int
    Supplier: str

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(InventoryBase):
    pass

class Inventory(InventoryBase):
    ProductID: str
    model_config = {
        "from_attributes": True
    }

##############################3

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
    #riskID: int hopefully this works w/out primary key
    model_config = {
        "from_attributes": True
    }

###########################3

class InvoiceBase(BaseModel):
    OrderDate: date
    ShipDate: date
    DueDate: date
    SalesOrderNo: str
    ShippingHandling: float
    TotalAmt: float
    Supplier: str
    #File: ...

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    InvoiceNumber: str
    model_config = {
        "from_attributes": True
    }


###############################
class SupplierBase(BaseModel):
    #SupplierName: str
    ContactName: str
    ContactEmail: str
    ContactPhone: str

# class SupplierCreate(SupplierBase):
#     pass
#
# class SupplierUpdate(SupplierBase):
#     pass

class Supplier(SupplierBase):
    SupplierName: str
    model_config = {
        "from_attributes": True
    }
    
