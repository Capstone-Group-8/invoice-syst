import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001";

function App() {
  const [invoices, setInvoices] = useState([]);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [lineItems, setLineItems] = useState([]);
  const [status, setStatus] = useState("Connecting to backend...");

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

  async function viewInvoice(invoice) {
    setSelectedInvoice(invoice);
    setLineItems([]);
    try {
      const response = await fetch(`${API}/invoices/${invoice.InvoiceNumber}/lineitems`);
      if (!response.ok) throw new Error();
      setLineItems(await response.json());
    } catch {
      setStatus("Invoice loaded, but line items could not be retrieved.");
    }
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
                      <button onClick={() => viewInvoice(invoice)}>Review</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedInvoice && (
        <section className="panel">
          <h2>Invoice {selectedInvoice.InvoiceNumber}</h2>
          <div className="summary-grid">
            <span><strong>Supplier:</strong> {selectedInvoice.Supplier}</span>
            <span><strong>Due:</strong> {selectedInvoice.DueDate}</span>
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
    </main>
  );
}

export default App;
