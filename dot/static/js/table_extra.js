// Thanks for Calumah: https://stackoverflow.com/users/1079254/calumah
// Quick and simple export target #table_id into a csv
function download_table_as_csv(table_id, separator = ',') {
  // Select rows from table_id
  var rows = document.querySelectorAll('table#' + table_id + ' tr');
  // Construct csv
  var csv = [];
  for (var i = 0; i < rows.length; i++) {
    var row = [], cols = rows[i].querySelectorAll('td, th');
    for (var j = 0; j < cols.length; j++) {
      // Clean innertext to remove multiple spaces and jumpline (break csv)
      var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
      // Remove acentuação de caracteres
      // data = data.normalize("NFD").replace(/[^a-zA-Zs|' ']/g, "");
      data = data.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
      data = data.replace(/"/g, '""');
      // Push escaped string
      row.push('"' + data + '"');
    }
    csv.push(row.join(separator));
  }
  var csv_string = csv.join('\n');
  // Download it
  var filename = 'export_' + table_id + '_' + new Date().toLocaleDateString() + '.csv';
  var link = document.createElement('a');
  link.style.display = 'none';
  link.setAttribute('target', '_blank');
  link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv_string));
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Thanks for Dom https://www.youtube.com/c/dcode-software/about [dcodeyt45@gmail.com]
function sortTable(table, column, asc=true) {
  const modifier = asc ? 1 : -1;
  const tBody = table.tBodies[0];
  const rows = Array.from(tBody.querySelectorAll("tr"));
  
  const sortedRows = rows.sort((a, b) => {
    const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
    const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
    
    return aColText > bColText ? (1 * modifier) : (-1 * modifier);
  });
  
  tBody.innerHTML = ''; // Limpa das rows da tabela
  tBody.append(...sortedRows); // Reinsere as linhas
  
  table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
  table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
  table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);
}

document.querySelectorAll(".table-sortable th").forEach(headerCell => {
  headerCell.addEventListener("click", () => {
    const tableElement = headerCell.parentElement.parentElement.parentElement;
    const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
    const currentIsAscending = headerCell.classList.contains("th-sort-asc");
    
    sortTable(tableElement, headerIndex, !currentIsAscending);
  });
});
