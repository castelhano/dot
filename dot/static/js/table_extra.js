function download_table_as_csv(table_id, separator = ';', clean=false) {
  // Thanks for Calumah: https://stackoverflow.com/users/1079254/calumah
  var rows = document.querySelectorAll('table#' + table_id + ' tr');
  
  var csv = [];
  for (var i = 0; i < rows.length; i++) {
    if(rows[i].style.display == 'none'){}
    else{
      var row = [], cols = rows[i].querySelectorAll('td, th');
      for (var j = 0; j < cols.length; j++) {
        var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' '); // Remove multiples espacos e quebra de linha
        if(clean){data = data.normalize("NFD").replace(/[\u0300-\u036f]/g, "");} // Remove acentuação de caracteres
        data = data.replace(/"/g, '""'); // Escape double-quote with double-double-quote (see https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv)
        row.push('"' + data + '"'); // Carrega string 'limpa'
      }
      csv.push(row.join(separator));
    }
  }
  var csv_string = csv.join('\n');
  // Download it
  var filename = 'export_' + table_id + '_' + new Date().toLocaleDateString() + '.csv';
  var link = document.createElement('a');
  link.style.display = 'none';
  link.setAttribute('target', '_blank');
  link.setAttribute('href', 'data:text/csv;charset=utf-8,%EF%BB%BF,' + encodeURIComponent(csv_string));
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

/* FUNÇÃO filterTable()
** @param table ID da tabela a ser filtarda
** @param cols Lista com ordem das colunas a submeter o filtro
** @param prefix String adicionada antes do criterio
** @param posfix String acidionada apos o criterio
*/
function filterTable(table_id, cols, input, prefix='', posfix=''){
  const table = document.getElementById(table_id);
  const filter = `${prefix}${input.value}${posfix}`.toLowerCase();
  let tr = table.tBodies[0].getElementsByTagName("tr");
  
  for (i = 0; i < tr.length; i++) {
    let row_value = '';
    for(j=0; j < cols.length;j++) {
      td = tr[i].getElementsByTagName("td")[cols[j]];
      row_value += td.textContent || td.innerText;
    }
    if (row_value.toLowerCase().indexOf(filter) > -1) {tr[i].style.display = "";}
    else {tr[i].style.display = "none";}
  }
}



