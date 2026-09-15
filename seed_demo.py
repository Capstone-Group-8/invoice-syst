from datetime import date

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        if not db.query(models.Supplier).filter(models.Supplier.SupplierName == "Bullseye Glass Co.").first():
            db.add(
                models.Supplier(
                    SupplierName="Bullseye Glass Co.",
                    ContactName="Demo Contact",
                    ContactEmail="demo@example.com",
                    ContactPhone="000-000-0000",
                )
            )

        if not db.query(models.Invoice).filter(models.Invoice.InvoiceNumber == "INV-DEMO-01").first():
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
                    ),
                    models.InvoiceLineItem(
                        InvoiceNumber="INV-DEMO-01",
                        Quantity=1,
                        SuppliersID="000124-0030-F-FULL",
                        SuppliersDesc="Red Full Double-Rolled",
                        Rate=55.83,
                        Amount=55.83,
                    ),
                ]
            )
        db.commit()
        print("Demo data is ready.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
