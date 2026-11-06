/* ==========================================================================
   EXPORT & PRINT HELPERS
   ========================================================================== */

function printPage() {
  window.print();
}

function exportTableToCSV(tableId, filename) {
  const table = document.getElementById(tableId);
  if (!table) return;

  const rows = table.querySelectorAll('tr');
  const csv = [];
  
  rows.forEach(row => {
    const cols = row.querySelectorAll('td, th');
    const rowData = [];
    cols.forEach(col => {
      // Clean up text
      let text = col.innerText.replace(/"/g, '""').trim();
      rowData.push(`"${text}"`);
    });
    csv.push(rowData.join(','));
  });

  const csvFile = new Blob([csv.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const downloadLink = document.createElement('a');
  downloadLink.download = `${filename || 'export'}.csv`;
  downloadLink.href = window.URL.createObjectURL(csvFile);
  downloadLink.style.display = 'none';
  document.body.appendChild(downloadLink);
  downloadLink.click();
  document.body.removeChild(downloadLink);
}
