import { useEffect, useState } from "react";
//import { createRoot } from 'react-dom/client';


const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

function App() {
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [lineItems, setLineItems] = useState([]);
  const [status, setStatus] = useState("Connecting to backend...");
  const [editable, setEditable] = useState(false);
  const [stDueDate, setStDueDate] = useState("");
  const [stSupplier, setStSupplier] = useState("");
  const [stInvoiceNum, setStInvoiceNum] = useState("");
  const [stOrderDate, setStOrderDate] = useState("");
  const [stShipDate, setStShipDate] = useState("");
  const [stSalesOrderNo, setStSalesOrderNo ] = useState("");
  const [stShipping, setStShipping] = useState("");
  const [stTotalAmt, setStTotalAmt] = useState("");

  useEffect(() => {
    fetch(`${API}/invoices/all`)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load invoices");
        return response.json();
      })
      .then((data) => {
        setInvoices(data);
        setStatus(data.length ? "" : "Backend connected. No invoices found yet.");
      })
      .catch(() => setStatus("Frontend is working. Backend is not connected yet."));
  }, []);

  async function displayInvoice(invoice) {
    setSelectedInvoice(invoice);
    console.log(JSON.stringify(selectedInvoice));
    setLineItems([]);
    try {
      const response = await fetch(`${API}/invoices/${invoice.InvoiceNumber}/lineitems`);
      if (!response.ok) throw new Error();
      setLineItems(await response.json());
      //console.log(editable);
    } catch {
      setStatus("Invoice loaded, but line items could not be retrieved.");
    }
  }

  function editInvoice(invoice) {
    setStInvoiceNum(selectedInvoice.InvoiceNumber);
    setStDueDate(selectedInvoice.DueDate);
    setStSupplier(selectedInvoice.Supplier);
    setStOrderDate(selectedInvoice.OrderDate);
    setStShipDate(selectedInvoice.ShipDate);
    setStShipping(selectedInvoice.ShippingHandling);
    setStSalesOrderNo(selectedInvoice.SalesOrderNo);
    setStTotalAmt(selectedInvoice.TotalAmt);
    setEditable(true);
    displayInvoice(invoice);

  }

  function viewInvoice(invoice) {
    setEditable(false);
    displayInvoice(invoice);
  }

  function update_form(e) {
    e.preventDefault();

    const invoice = {
        OrderDate: stOrderDate,
        ShipDate: stShipDate,
        DueDate: stDueDate,
        SalesOrderNo: stSalesOrderNo,
        ShippingHandling: stShipping,
        TotalAmt: stTotalAmt,
        Supplier: stSupplier
    };
    //console.log(JSON.stringify(invoice));

    const requestOptions = {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify(invoice)
    };

    fetch(`${API}/invoices/${stInvoiceNum}`, requestOptions)
    .then(res => res.json())
    .then(() => {
        window.location.reload(false);
    });
}

  return (
    <main className="page">
      <header>
        <p className="eyebrow">Capstone Group 8</p>
        <h1>Invoice Processing System</h1>
        <p className="subtitle">Human-in-the-loop review of workplace invoice data.</p>
        
      </header>

      {status && <div className="status">{status}</div>}

      <section className="panel">

        <h2>Invoices</h2>
        {invoices.length > 0 && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Supplier</th>
                  <th>Order Date</th>
                  <th>Total</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((invoice) => (
                  <tr key={invoice.InvoiceNumber}>
                    <td>{invoice.InvoiceNumber}</td>
                    <td>{invoice.Supplier}</td>
                    <td>{invoice.OrderDate}</td>
                    <td>${Number(invoice.TotalAmt).toFixed(2)}</td>
                    <td>
                      <button onClick={() => viewInvoice(invoice)}>View</button> 
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedInvoice && !editable && (
        <section className="panel">
          <h2>Invoice {selectedInvoice.InvoiceNumber}</h2>
          <p><button onClick={() => editInvoice(selectedInvoice)}>Edit</button></p>
          <div className="summary-grid">
            <span><strong>Supplier:</strong> {selectedInvoice.Supplier}</span>
            <span><strong>Order Date: </strong> {selectedInvoice.OrderDate}</span>
            <span><strong>Sales Order:</strong> {selectedInvoice.SalesOrderNo}</span>
            <span><strong>Due:</strong> {selectedInvoice.DueDate}</span>
            <span><strong>Shipped On:</strong> {selectedInvoice.ShipDate} </span>
          </div>
          <div className="summary-grid">
            <span><strong>Shipping:</strong> ${Number(selectedInvoice.ShippingHandling).toFixed(2)}</span>
            <span><strong>Total:</strong> ${Number(selectedInvoice.TotalAmt).toFixed(2)}</span>
          </div>
          <h3>Line Items</h3>
          {lineItems.length === 0 ? (
            <p>No line items available.</p>
          ) : (
            lineItems.map((item) => (
              <div className="line-item" key={`${item.InvoiceNumber}-${item.SuppliersID}`}>
                <div>
                  <strong>{item.SuppliersDesc}</strong>
                  <small>{item.SuppliersID}</small>
                </div>
                <span>{item.Quantity} × ${Number(item.Rate).toFixed(2)} = ${Number(item.Amount).toFixed(2)}</span>
              </div>
            ))
          )}
        </section>
      )}


      {selectedInvoice && editable && (
        <section className="panel">
          <form name='form1' onSubmit={update_form}>
          <div className="summary-grid">
            {/*<span>
              <label htmlFor="invoice_num">Invoice Number: </label> 
              <input type="text" className="form-control" id="invoice_num" name = "invoice_num" defaultValue={selectedInvoice.InvoiceNumber} required></input>
            </span>*/}
            <span>
              <label htmlFor="supplier">Supplier:</label> 
              <input type="text" className="form_control" id="supplier" name="supplier" 
              value={stSupplier} required 
              onChange={(e) => setStSupplier(e.target.value)}/>
            </span>
            <span>
              <label htmlFor="order_date">Order Date: </label>
              <input type="date" className="form-control" id="order_date" name = "order_date" 
              value={stOrderDate} required
              onChange={(e) => setStOrderDate(e.target.value)}/>
            </span>
            <span>
              <label htmlFor="sales_order">Sales Order: </label>
              <input type="text" className="form-control" id="sales_order" name = "sales_order" 
              value={stSalesOrderNo} required
              onChange={(e) => setStSalesOrderNo(e.target.value)}/>
            </span>
            <span>
              <label htmlFor="due_date">Due: </label>
              <input type="date" className="form-control" id="due_date" name = "due_date" 
              value={stDueDate} required
              onChange={(e) => setStDueDate(e.target.value)}/>
            </span>
            <span>
              <label htmlFor="ship_date">Shipped On: </label>
              <input type="date" className="form-control" id="ship_date" name = "ship_date" 
              value={stShipDate} required
              onChange={(e) => setStShipDate(e.target.value)}/>
            </span>
          </div>
          <div className="summary-grid">
            <span>
              <label htmlFor="shipping">Shipping and Handling:</label>
              <input type="number" className="form_control" id="shipping" name="shipping" step = "0.01" min="0"
              value={stShipping} required
                onChange={(e) => setStShipping(e.target.value)}/>   
            </span>
            <span>
              <label htmlFor="total">Total:</label>
              <input type="number" className="form_control" id="total" name="total" step="0.01" min="0"
              value={stTotalAmt} required
              onChange={(e) => setStTotalAmt(e.target.value)}/>    
            </span>
          </div>
          <input type="submit" />
          </form>
          <h3>Line Items</h3>
          {lineItems.length === 0 ? (
            <p>No line items available.</p>
          ) : (
            lineItems.map((item) => (
              <div className="line-item" key={`${item.InvoiceNumber}-${item.SuppliersID}`}>
                <div>
                  <strong>{item.SuppliersDesc}</strong>
                  <small>{item.SuppliersID}</small>
                </div>
                <span>{item.Quantity} × ${Number(item.Rate).toFixed(2)} = ${Number(item.Amount).toFixed(2)}</span>
              </div>
            ))
          )}
        </section>
      )}
      
    </main>
  );
}

export default App;
