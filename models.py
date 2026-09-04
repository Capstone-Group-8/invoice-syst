from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Inventory(Base):
    __tablename__ = "Inventory" 

    ProductID = Column(String(10), primary_key=True, index=True)
    SuppliersID = Column(String(50), nullable=True)
    Description = Column(String(120), nullable=False)
    ProductType = Column(String(20), nullable=False)
    QtyOnHand = Column(Integer, nullable=False)
    LastPrice = Column(Float, nullable=True)
    TotalQtyDesired = Column(Integer, nullable=True)
    Supplier = Column(String(50), nullable=True)

class InvoiceLineItem(Base):
    __tablename__ = "InvoiceLineItems" 
    
    InvoiceNumber = Column(String(10), nullable=False, primary_key=True)
    Quantity = Column(Integer, nullable=False)
    SuppliersID = Column(String(50), nullable=False, primary_key=True)
    SuppliersDesc = Column(String(120), nullable=False)
    Rate = Column(Float, nullable=False)
    Amount = Column(Float, nullable=False)

class Invoice(Base):
    __tablename__ = "Invoices"

    InvoiceNumber = Column(String(50), primary_key=True, index=True)
    OrderDate = Column(Date, nullable=False)
    ShipDate = Column(Date, nullable=False)
    DueDate = Column(Date, nullable=False)
    SalesOrderNo = Column(String(50), nullable=False)
    ShippingHandling = Column(Float, nullable=False)
    TotalAmt = Column(Float, nullable=False)
    Supplier = Column(String(20), nullable=False)
    #File = Column(Blob...
    
class Supplier(Base):
    __tablename__= "Suppliers"
    
    SupplierName = Column(String(50), primary_key=True, index=True)
    ContactName = Column(String(50), nullable=True)
    ContactEmail = Column(String(50), nullable=True)
    ContactPhone = Column(String(15), nullable=True)
