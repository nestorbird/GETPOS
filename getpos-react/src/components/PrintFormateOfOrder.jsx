import { forwardRef, useImperativeHandle } from 'react';

const PrintFormateOfOrder = forwardRef(({ doc }, ref) => {
  useImperativeHandle(ref, () => ({
    handlePrint
  }));

  const handlePrint = () => {
    const printContent = `
      <html>
        <head>
          <style>
            body {
              font-family: Arial, sans-serif;
              font-size: 14px;
            }
            .container {
              border: 1px solid black;
              padding: 5%;
              width: 50%;
              display: flex;
              flex-direction: column;
              justify-content: center;
              align-items: center;
              margin: auto;
            }
            .line {
              border-bottom: 1px dotted black;
              text-align: center;
              width: 100%;
              margin-bottom: 15px;
              padding-bottom: 10px;
            }
            .content {
              width: 100%;
            }
            .items {
              width: 100%;
              margin-bottom: 15px;
            }
            .items span {
              display: flex;
              justify-content: space-between;
              border-bottom: 1px dotted black;
              padding: 10px 0;
              font-size: 16px; 
            }
            .totals {
              width: 100%;
              margin-top: 15px;
            }
            .totals td {
              padding: 10px;
              font-size: 16px; 
            }
            .totals .label {
              text-align: right;
              width: 70%;
            }
            .totals .value {
              text-align: right;
              width: 30%;
            }
            .footer {
              text-align: center;
              width: 100%;
              border-top: 1px solid black;
              margin-top: 15px;
              padding-top: 10px;
            }
          </style>
        </head>
        <body>
          <section class="container">
            <div class="line">
              <h1>GETPOS</h1>
              <p>Address: 123 Main St, City, Country</p>
            </div>
            <div class="content">
              <p>Check#: ${doc.name}</p>
              <p>Date: ${doc.transaction_date} - ${doc.transaction_time}</p>
              <p>Cashier: ${doc.hub_manager_name}</p>
              <div class="items">
                ${doc.items.map((item, index) => `
                  <span key=${index}>
                    <p>${index + 1}</p>
                    <p>${item.item_code} - ${item.item_name}</p>
                    <p>Qty: ${item.qty}</p>
                    <p>Rate: ${item.rate}</p>
                  </span>
                `).join('')}
              </div>
              <table class="totals">
                <tr>
                  <td class="label">Sub-total</td>
                  <td class="value">${doc.total}</td>
                </tr>
                <tr>
                  <td class="label">Discount ${doc.discount_percentage}%</td>
                  <td class="value">-${doc.discount_amount}</td>
                </tr>
                <tr>
                  <td class="label"><strong>Total</strong></td>
                  <td class="value"><strong>${doc.grand_total}</strong></td>
                </tr>
              </table>
            </div>
            <div class="footer">
              <p>GETPOS</p>
              <p>Thank You. Please come again</p>
              <p>Date: ${doc.transaction_date}</p>
            </div>
          </section>
        </body>
      </html>
    `;

    const printWindow = window.open('', '_blank');
    printWindow.document.open();
    printWindow.document.write(printContent);
    printWindow.document.close();
    printWindow.onload = function() {
      printWindow.print();
    };
  };

  return null; 
});

export default PrintFormateOfOrder;
