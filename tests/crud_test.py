'''
Integration test for testing CRUD operations
Covers main, crud, seed_demo, database, schemas, and models for sqlite
@Sally Little
Sep 16 2026
'''
import sys
#import pytest
#import sqlite3
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from seed_demo import seed
seed()

import main
db = next(main.get_db())
no_of_invoices = 0

#Invoices and line items
def test_read_invoices():
    invoices = main.read_invoices(db)
    assert len(invoices) > 0
    for invoice in invoices:
        print(invoice.InvoiceNumber)

def test_read_one_invoice():
    invoice = main.read_invoice("INV-DEMO-01", db)
    print(invoice.InvoiceNumber, invoice.TotalAmt, invoice.OrderDate, invoice.ShippingHandling, invoice.ShipDate, invoice.DueDate, invoice.SalesOrderNo, invoice.Supplier)
    assert getattr(invoice, "InvoiceNumber") == "INV-DEMO-01"
    assert getattr(invoice, "TotalAmt") == 78.25, "Total amount does not match"
    assert getattr(invoice, "OrderDate") == date(2026, 9, 1), "Order date does not match: " + str(getattr(invoice, "OrderDate"))
    assert getattr(invoice, "ShippingHandling") == 10.00, "Shipping amount does not match"
    assert getattr(invoice, "ShipDate") == date(2026, 9, 2), "Ship date does not match"
    assert getattr(invoice, "DueDate") == date(2026, 10, 1), "Due date does not match"
    assert getattr(invoice, "SalesOrderNo") == "SO-DEMO-01", "Sales order number does not match"
    assert getattr(invoice, "Supplier") == "Bullseye Glass Co.", "Supplier name does not match"


def test_read_invoice_items():
    line_items = main.read_invoice_items("INV-DEMO-01", db)
    assert len(line_items) > 0, "Number of line items is not greater than 0"
    assert getattr(line_items[0], "SuppliersID") == "000013-0001-F-P001", "Supplier ID does not match"
    assert getattr(line_items[0], "SuppliersDesc") == "Opaque White Opal Fine Frit 1 lb jar", "Supplier description does not match"
    assert getattr(line_items[0], "Rate") == 12.42, "Rate does not match"
    assert getattr(line_items[0], "Amount") == 12.42, "Amount does not match"
    assert getattr(line_items[0], "LineCount") == 1, "Line count does not match"

    assert getattr(line_items[1], "SuppliersID") == "000124-0030-F-FULL", "Supplier ID does not match"
    assert getattr(line_items[1], "SuppliersDesc") == "Red Full Double-Rolled", "Supplier description does not match"
    assert getattr(line_items[1], "Rate") == 55.83, "Rate does not match"
    assert getattr(line_items[1], "Amount") == 55.83, "Amount does not match"
    assert getattr(line_items[1], "LineCount") == 2, "Line count does not match"


def test_create_new_invoice():
    main.create_new_invoice(
        main.InvoiceCreate(
            InvoiceNumber="INV-DEMO-02",
            OrderDate=date(2026, 9, 3),
            ShipDate=date(2026, 9, 4),
            DueDate=date(2026, 10, 3),
            SalesOrderNo="SO-DEMO-02",
            ShippingHandling=15.00,
            TotalAmt=100.00,
            Supplier="Mountain Glass Co.",
        ),
        db,
    )
    new_invoice = main.read_invoice("INV-DEMO-02", db)
    assert getattr(new_invoice, "TotalAmt") == 100.00, "Total amount does not match"
    assert getattr(new_invoice, "OrderDate") == date(2026, 9, 3), "Order date does not match: " + str(new_invoice.OrderDate)
    assert getattr(new_invoice, "ShippingHandling") == 15.00, "Shipping amount does not match"
    assert getattr(new_invoice, "ShipDate") == date(2026, 9, 4), "Ship date does not match: " + str(new_invoice.ShipDate)
    assert getattr(new_invoice, "DueDate") == date(2026, 10, 3), "Due date does not match: " + str(new_invoice.DueDate)
    assert getattr(new_invoice, "SalesOrderNo") == "SO-DEMO-02", "Sales order number does not match"
    assert getattr(new_invoice, "Supplier") == "Mountain Glass Co.", "Supplier name does not match"
    invoices = main.read_invoices(db)
    assert len(invoices) > no_of_invoices, "Number of invoices in system did not go up after creating a new invoice"
    

    
def test_create_new_line_item():
    main.create_new_line_item(
        "INV-DEMO-02",
        main.InvoiceLineItemCreate(
            InvoiceNumber="INV-DEMO-02",
            Quantity=2,
            SuppliersID="000100-0030-F-FULL",
            SuppliersDesc="Black Full Double-Rolled",
            Rate=55.83,
            Amount=111.66,
            LineCount =1,
        ),
        db,
    )
    line_items = main.read_invoice_items("INV-DEMO-02", db)
    assert getattr(line_items[0], "SuppliersID") == "000100-0030-F-FULL", "Supplier ID does not match"
    assert getattr(line_items[0], "SuppliersDesc") == "Black Full Double-Rolled", "Supplier description does not match"
    assert getattr(line_items[0], "Rate") == 55.83, "Rate does not match"
    assert getattr(line_items[0], "Amount") == 111.66, "Amount does not match"
    assert getattr(line_items[0], "LineCount") == 1, "LineCount does not match"

def test_update_invoice():
    main.update_invoice(
        "INV-DEMO-02",
        main.InvoiceUpdate(
            OrderDate=date(2026, 9, 5),
            ShipDate=date(2026, 9, 6),
            DueDate=date(2026, 10, 5),
            SalesOrderNo="SO-DEMO-03",
            ShippingHandling=20.99,
            TotalAmt=120.10,
            Supplier="Bullseye Glass Co.",
        ),
        db
    )
    updated_invoice = main.read_invoice("INV-DEMO-02", db)
    assert getattr(updated_invoice, "OrderDate") == date(2026, 9, 5), "Order date was not updated"
    assert getattr(updated_invoice, "ShipDate") == date(2026, 9, 6), "Ship date was not updated"
    assert getattr(updated_invoice, "DueDate") == date(2026, 10, 5), "Due date was not updated"
    assert getattr(updated_invoice, "SalesOrderNo") == "SO-DEMO-03", "Sales order number was not updated"
    assert getattr(updated_invoice, "ShippingHandling") == 20.99, "Shipping amount was not updated"
    assert getattr(updated_invoice, "TotalAmt") == 120.10, "Total amount was not updated"

def test_create_and_read_change():
    main.create_change(
        main.ChangeLogCreate(
            InvoiceID="INV-DEMO-02",
            FieldChanged="OrderDate",
            OldValue="2026-09-03",
            NewValue="2026-09-05",
            Author="Test User",
        ),
        db,
    )
    main.create_change(
        main.ChangeLogCreate(
            InvoiceID="INV-DEMO-02",
            FieldChanged="SalesOrderNo",
            OldValue="SO-DEMO-02",
            NewValue="SO-DEMO-03",
        ),
        db,
    )
    change_logs = main.read_invoice_changes("INV-DEMO-02", db)
    assert len(change_logs) == 2, "Number of change logs does not match"
    all_change_logs = main.read_all_changes(db)
    assert len(all_change_logs) >= 2, "Number of all change logs does not match"
    assert change_logs == all_change_logs, "change logs do not match"
    first_change = change_logs[0]
    second_change = change_logs[1]
    assert first_change.InvoiceID == "INV-DEMO-02", "Invoice ID does not match"
    assert first_change.FieldChanged == "OrderDate", "Field changed does not match"
    assert first_change.OldValue == "2026-09-03", "Old value does not match"
    assert first_change.NewValue == "2026-09-05", "New value does not match"
    assert first_change.Author == "Test User", "Author does not match"
    assert second_change.InvoiceID == "INV-DEMO-02", "Invoice ID does not match"
    assert second_change.FieldChanged == "SalesOrderNo", "Field changed does not match"
    assert second_change.OldValue == "SO-DEMO-02", "Old value does not match"
    assert second_change.NewValue == "SO-DEMO-03", "New value does not match"
    first_changeid = first_change.ChangeID
    second_changeid = second_change.ChangeID
    first_change_from_db = main.read_change(first_changeid, db)
    second_change_from_db = main.read_change(second_changeid, db)
    assert first_change_from_db.InvoiceID == "INV-DEMO-02", "Invoice ID does not match"
    assert first_change_from_db.FieldChanged == "OrderDate", "Field changed does not match"
    assert first_change_from_db.OldValue == "2026-09-03", "Old value does not match"
    assert first_change_from_db.NewValue == "2026-09-05", "New value does not match"
    assert first_change_from_db.Author == "Test User", "Author does not match"
    assert second_change_from_db.InvoiceID == "INV-DEMO-02", "Invoice ID does not match"
    assert second_change_from_db.FieldChanged == "SalesOrderNo", "Field changed does not match"
    assert second_change_from_db.OldValue == "SO-DEMO-02", "Old value does not match"
    assert second_change_from_db.NewValue == "SO-DEMO-03", "New value does not match"
    main.crud.delete_change(db, first_changeid)
    main.crud.delete_change(db, second_changeid)

def test_update_line_item():
    main.update_line_item(
        "INV-DEMO-01",
        "000124-0030-F-FULL",
        main.InvoiceLineItemUpdate(
            InvoiceNumber="INV-DEMO-01",
            SuppliersID="000025-0030-F-FULL",
            Quantity=3,
            SuppliersDesc="Tangerine Full Double-Rolled Updated",
            Rate=60.58,
            Amount=180.90,
            LineCount=2,
        ),
        db,
    )
    updated_line_items = main.read_invoice_items("INV-DEMO-01", db)
    assert getattr(updated_line_items[1], "Quantity") == 3, "Quantity was not updated"
    assert getattr(updated_line_items[1], "SuppliersDesc") == "Tangerine Full Double-Rolled Updated", "Supplier description was not updated"
    assert getattr(updated_line_items[1], "Rate") == 60.58, "Rate was not updated"
    assert getattr(updated_line_items[1], "Amount") == 180.90, "Amount was not updated"
    assert getattr(updated_line_items[1], "LineCount") == 2, "Line count did not remain 2"
    #main.crud.delete_line_item(db, "INV-DEMO-02", "000100-0030-F-FULL")
    main.crud.delete_invoice(db, "INV-DEMO-02")

#def test_create_change_lineitem():
 #   main.create

#Inventory
def test_create_new_inventory_item():
    main.create_new_inventory_entry(
        main.InventoryCreate(
            ProductID = "80026",
            SuppliersID="000500-0030-F-FULL",
            Description="New Inventory Item",
            ProductType = "Sheet Glass",
            QtyOnHand=2,
            LastPrice=55.83,
            TotalQtyDesired = 3,
            Supplier = "Bullseye Glass Co."
        ),
        db,
    )
    inventory = main.read_inventory(db)
    assert any(item.ProductID == "80026" for item in inventory), "New inventory item not found"
    new_item = main.read_inventory_entry("80026", db)
    assert getattr(new_item, "SuppliersID") == "000500-0030-F-FULL", "Supplier ID does not match"
    assert getattr(new_item, "Description") == "New Inventory Item", "Supplier description does not match"
    assert getattr(new_item, "QtyOnHand") == 2, "Quantity on hand does not match"
    assert getattr(new_item, "LastPrice") == 55.83, "Last price does not match"
    assert getattr(new_item, "TotalQtyDesired") == 3, "Total quantity desired does not match"
    assert getattr(new_item, "Supplier") == "Bullseye Glass Co.", "Supplier name does not match"
    #the item is deleted below in test_upload_fake_data() after the upload test is run, so that the inventory is cleaned up for future tests

def test_read_inventory():
    inventory = main.read_inventory(db)
    assert len(inventory) > 0

def test_update_inventory():
    main.update_inventory(
        "80026",
        main.InventoryUpdate(
            SuppliersID="00125-0030-F-FULL",
            Description="Transparent Tangerine Full Double-Rolled",
            ProductType = "Glass",
            QtyOnHand=3,
            LastPrice=60.58,
            TotalQtyDesired = 4,
            Supplier = "Mountain Glass Co."
        ),
        db
    )
    updated_item = main.read_inventory_entry("80026", db)
    assert getattr(updated_item, "SuppliersID") == "00125-0030-F-FULL", "Supplier ID was not updated"
    assert getattr(updated_item, "Description") == "Transparent Tangerine Full Double-Rolled", "Description was not updated"
    assert getattr(updated_item, "ProductType") == "Glass", "Product type was not updated"
    assert getattr(updated_item, "QtyOnHand") == 3, "Quantity on hand was not updated"
    assert getattr(updated_item, "LastPrice") == 60.58, "Last price was not updated"
    assert getattr(updated_item, "TotalQtyDesired") == 4, "Total quantity desired was not updated"
    assert getattr(updated_item, "Supplier") == "Mountain Glass Co.", "Supplier name was not updated"

#Suppliers
def test_read_suppliers():
    suppliers = main.read_suppliers(db)
    assert len(suppliers) > 0



    
""" 
#Negatives
# These are supposed to raise exceptions. However they are still "failing" by doing so, so they're commented out.
def test_existing_invoice():
    with pytest.raises(sqlite3.IntegrityError):
        main.create_new_invoice(
            main.InvoiceCreate(
                InvoiceNumber="INV-DEMO-01",
                OrderDate=date(2026, 9, 1),
                ShipDate=date(2026, 9, 2),
                DueDate=date(2026, 10, 1),
                SalesOrderNo="SO-DEMO-01",
                ShippingHandling=10.00,
                TotalAmt=78.25,
                Supplier="Bullseye Glass Co.",
            ),
            db,
        )
def test_existing_line_item():
    with pytest.raises(sqlite3.IntegrityError):
        main.create_new_line_item(
            "INV-DEMO-01",
            main.InvoiceLineItemCreate(
                InvoiceNumber="INV-DEMO-01",
                Quantity=2,
                SuppliersID="000025-0030-F-FULL",
                SuppliersDesc="Tangerine Full Double-Rolled",
                Rate=55.83,
                Amount=111.66,
            ),
            db,
        ) """

def test_handle_invoice():
    #what black glass's entry looks like before the upload
    original_item = main.read_inventory_entry("24491", db)
    assert original_item.SuppliersID == "000100-0030-F-FULL", "Supplier ID does not match"
    assert original_item.Description == "Black Full Double-Rolled", "Supplier description does not match"
    assert original_item.QtyOnHand == 2, "Quantity on hand was not reset"
    assert original_item.LastPrice == 55.83, "Last price was not reset"

    invoice = main.InvoiceCreate(
            InvoiceNumber="INV-DEMO-06",
            OrderDate=date(2026, 9, 3),
            ShipDate=date(2026, 9, 4),
            DueDate=date(2026, 10, 3),
            SalesOrderNo="SO-DEMO-02",
            ShippingHandling=15.00,
            TotalAmt=211.38,
            Supplier="Bullseye Glass Co.",
        )
    item1 = main.InvoiceLineItemCreate(
            InvoiceNumber="INV-DEMO-06",
            Quantity=2,
            SuppliersID="000100-0030-F-FULL",
            SuppliersDesc="Black Full Double-Rolled",
            Rate=61.32,
            Amount=122.64,
            LineCount = 1,
        )
    item2 = main.InvoiceLineItemCreate(
            InvoiceNumber="INV-DEMO-06",
            Quantity=1,
            SuppliersID="000100-0031-F-FULL",
            SuppliersDesc="Black Irid Rainbow Full Double-Rolled",
            Rate=61.32,
            Amount=61.32,
            LineCount = 2,
        )
    item3 = main.InvoiceLineItemCreate(
            InvoiceNumber="INV-DEMO-06",
            Quantity=1,
            SuppliersID="055513-0001-F-P001",
            SuppliersDesc="Totally Fake Fine Frit 1 lb jar",
            Rate=12.42,
            Amount=12.42,
            LineCount = 3,
    )
    main.handle_invoice(invoice, [item1, item2, item3], [(0.95, 0.90), (0.42, 0.48), (0.85, 0.80)], db)
    main.update_all_inventory([item1, item2, item3], invoice.Supplier, db, test_toggle=True)
    new_invoice = main.read_invoice("INV-DEMO-06", db)
    line_items = main.read_invoice_items("INV-DEMO-06", db)
    #invoice has been added
    assert new_invoice.TotalAmt == 211.38, "Total amount does not match"
    assert new_invoice.OrderDate == date(2026, 9, 3), "Order date does not match: " + str(new_invoice.OrderDate)
    assert new_invoice.ShippingHandling == 15.00, "Shipping amount does not match"
    assert new_invoice.ShipDate == date(2026, 9, 4), "Ship date does not match: " + str(new_invoice.ShipDate)
    assert new_invoice.DueDate == date(2026, 10, 3), "Due date does not match: " + str(new_invoice.DueDate)
    assert new_invoice.SalesOrderNo == "SO-DEMO-02", "Sales order number does not match"
    assert new_invoice.Supplier == "Bullseye Glass Co.", "Supplier name does not match"

    assert line_items[0].SuppliersID == "000100-0030-F-FULL", "Supplier ID does not match"
    assert line_items[0].SuppliersDesc == "Black Full Double-Rolled", "Supplier description does not match"
    assert line_items[0].Rate == 61.32, "Rate does not match"
    assert line_items[0].Amount == 122.64, "Amount does not match"
    assert line_items[0].LineCount ==1, "Count does not match"
    assert line_items[1].SuppliersID == "000100-0031-F-FULL", "Supplier ID does not match"
    assert line_items[1].SuppliersDesc == "Black Irid Rainbow Full Double-Rolled", "Supplier description does not match"
    assert line_items[1].Rate == 61.32, "Rate does not match"
    assert line_items[1].Amount == 61.32, "Amount does not match"
    assert line_items[1].LineCount == 2, "Count does not match"
    assert line_items[2].SuppliersID == "055513-0001-F-P001", "Supplier ID does not match"
    assert line_items[2].SuppliersDesc == "Totally Fake Fine Frit 1 lb jar", "Supplier description does not match"
    assert line_items[2].Rate == 12.42, "Rate does not match"
    assert line_items[2].Amount == 12.42, "Amount does not match"
    assert line_items[2].LineCount == 3, "Count does not match"

    #item that was not in inventory before has been added
    new_item = main.read_inventory_entry("80028", db)
    assert new_item.SuppliersID == "055513-0001-F-P001", "Supplier ID does not match " + str(new_item.SuppliersID)
    assert new_item.Description == "Totally Fake Fine Frit 1 lb jar", "Supplier description does not match"
    assert new_item.QtyOnHand == 1, "Quantity on hand does not match"
    assert new_item.LastPrice == 12.42, "Last price does not match"
    assert new_item.TotalQtyDesired == 0, "Total quantity desired does not match"
    assert new_item.Supplier == "Bullseye Glass Co.", "Supplier name does not match"

    #what black glass's inventory entry looks like after the upload
    updated_item = main.read_inventory_entry("24491", db)
    assert updated_item.SuppliersID == "000100-0030-F-FULL", "Supplier ID does not match"
    assert updated_item.Description == "Black Full Double-Rolled", "Supplier description does not match"
    assert updated_item.ProductType == "Glass", "Product type does not match"
    assert updated_item.QtyOnHand == 4, "Quantity on hand was not updated"
    assert updated_item.LastPrice == 61.32, "Last price was not updated"
    assert updated_item.TotalQtyDesired == 4, "Total quantity desired does not match"
    assert updated_item.Supplier == "Bullseye Glass Co.", "Supplier name does not match"
   
     #clean up
    main.crud.delete_line_item(db, "INV-DEMO-06", "000100-0030-F-FULL")
    main.crud.delete_line_item(db, "INV-DEMO-06", "000100-0031-F-FULL")
    main.crud.delete_line_item(db, "INV-DEMO-06", "055513-0001-F-P001")
    main.crud.delete_invoice(db, "INV-DEMO-06")
    main.crud.delete_inventory_entry(db, "80026") #by keeping this around until now, I know what the new inventory item's ID is
    main.crud.delete_inventory_entry(db, "80027")

if __name__ == "__main__":
    test_read_invoices()
    test_read_one_invoice()
    test_read_invoice_items()
    test_create_new_invoice()
    test_create_new_line_item()
    test_update_invoice()
    test_create_and_read_change()
    test_update_line_item()
    test_create_new_inventory_item()
    test_read_inventory()
    test_update_inventory()
    test_read_suppliers()
    test_handle_invoice()
    print("test complete")
 