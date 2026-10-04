from datetime import date

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        item = db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-01").first()
        if item:
            db.delete(item)
        item2 = db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-02").first()
        if item2:
            db.delete(item2)
        item6 = db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-06").first()
        if item6:
            db.delete(item6)

        items = db.query(models.InvoiceLineItem).filter(models.InvoiceLineItem.InvoiceNumber == "INV-DEMO-01").all()
        for line_item in items:
            db.delete(line_item)
        items2 = db.query(models.InvoiceLineItem).filter(models.InvoiceLineItem.InvoiceNumber == "INV-DEMO-02").all()
        for line_item in items2:
            db.delete(line_item) 
        items4 = db.query(models.InvoiceLineItem).filter(models.InvoiceLineItem.InvoiceNumber == "INV-DEMO-06").all()
        for line_item in items4:
            db.delete(line_item) 

        for i in range(80025, 80029):
            item = db.query(models.Inventory).filter(models.Inventory.ProductID == str(i)).first()
            if item:
                db.delete(item)
 
        item4 = db.query(models.Inventory).filter(models.Inventory.SuppliersID == "055513-0001-F-P001").first()
        if item4:
            db.delete(item4)
        item5 = db.query(models.Inventory).filter(models.Inventory.SuppliersID == "000100-0030-F-FULL").first()
        if item5:
            db.delete(item5)
        db.commit()
        db.flush()
        assert db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-01").first() is None
        assert db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-02").first() is None
        assert db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-06").first() is None
        print("Cached data has been flushed. Preparing demo data.")

        if not db.query(models.Supplier).filter(models.Supplier.SupplierName == "Bullseye Glass Co.").first():
            db.add(
                models.Supplier(
                    SupplierName="Bullseye Glass Co.",
                    ContactName="Demo Contact",
                    ContactEmail="demo@example.com",
                    ContactPhone="000-000-0000",
                )
            )

        if not db.query(models.Inventory).filter(models.Inventory.SuppliersID == "000100-0030-F-FULL").first():
            db.add(
                models.Inventory(
                    ProductID = "24491",                   
                    SuppliersID="000100-0030-F-FULL",
                    Description="Black Full Double-Rolled",
                    ProductType="Glass",
                    QtyOnHand=2,
                    LastPrice=55.83,                      
                    TotalQtyDesired=4, 
                    Supplier="Bullseye Glass Co."
                )
            )

        db.add(
            models.Invoice(
                InvoiceNumber="INV-DEMO-01",
                OrderDate=date(2026, 9, 1),
                ShipDate=date(2026, 9, 2),
                DueDate=date(2026, 10, 1),
                SalesOrderNo="SO-DEMO-01",
                ShippingHandling=10.00,
                TotalAmt=78.25,
                Supplier="Bullseye Glass Co.",
            )
        )
        db.add_all(
            [
                models.InvoiceLineItem(
                    InvoiceNumber="INV-DEMO-01",
                    Quantity=1,
                    SuppliersID="000013-0001-F-P001",
                    SuppliersDesc="Opaque White Opal Fine Frit 1 lb jar",
                    Rate=12.42,
                    Amount=12.42,
                    LineCount = 1,
                ),
                models.InvoiceLineItem(
                    InvoiceNumber="INV-DEMO-01",
                    Quantity=1,
                    SuppliersID="000124-0030-F-FULL",
                    SuppliersDesc="Red Full Double-Rolled",
                    Rate=55.83,
                    Amount=55.83,
                    LineCount = 2,
                ),
            ]
        )
 

        db.commit()
        print("Demo data is ready.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
