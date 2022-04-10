/*
* RETORNA REGISTRO 'VISIVEIS' DA TABELA EM FORMATO CSV 
*
* @version  1.0
* @since    02/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} table_id ID DA TABELA A SER CONVERTIDA
* @returns  {File.csv} Retorna arquivo da tabela formatado em csv
* @example  <a id="download" onclick="download_table_as_csv('main_table',';',true)">Exportar CSV</a>
* @see      {@link https://stackoverflow.com/users/1079254/calumah}
* @see      {@link https://stackoverflow.com/questions/17808511/properly-escape-a-double-quote-in-csv}
*/
function download_table_as_csv(table_id, separator = ';', clean=false) {
  var rows = document.querySelectorAll('table#' + table_id + ' tr');
  var csv = [];
  for (var i = 0; i < rows.length; i++) {
    if(rows[i].style.display == 'none'){}
    else{
      var row = [], cols = rows[i].querySelectorAll('td, th');
      for (var j = 0; j < cols.length; j++) {
        var data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' '); // Remove espacos multiplos e quebra de linha
        if(clean){data = data.normalize("NFD").replace(/[\u0300-\u036f]/g, "");} // Remove acentuação e caracteres especiais
        data = data.replace(/"/g, '""'); // Escape double-quote com double-double-quote 
        row.push('"' + data + '"'); // Carrega string
      }
      csv.push(row.join(separator));
    }
  }
  var csv_string = csv.join('\n');
  var filename = 'export_' + table_id + '_' + new Date().toLocaleDateString() + '.csv';
  var link = document.createElement('a');
  link.style.display = 'none';
  link.setAttribute('target', '_blank');
  link.setAttribute('href', 'data:text/csv;charset=utf-8,%EF%BB%BF' + encodeURIComponent(csv_string));
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

/*
* IMPLEMENTA FUNCAO PARA CLASSIFICAR TABELAS (vertical) AO CLICAR NO CABECALHO
*
* @version  1.0
* @since    02/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Adicione a classe table-sortable a tabela, requerer cabecalhos usando tag 'th' e conteudo dentro da 'tbody'
* @require  dot.css [classes de formação dos cabecalhos]
* @example
* <table class="table-sortable">
* <thead><th>Nome</th>.....</thead>
* <tbody>
*   <tr><td>Maria</td><td>22</td></tr>
*   <tr><td>Joao</td><td>25</td></tr>
*   ....
* </tbody>
* @see      {@link https://www.youtube.com/c/dcode-software/about}
*/
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

/*
* FILTRA LINHAS DA TABELA BASEADO NO CONTEUDO
*
* @version  1.0
* @since    02/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Adicione um input com chamada da funcao no evento onkeyup 
* @param    {String} table_id ID da tabela a ser filtrada
* @param    {Array} cols Lista com o indice das coluas a serem analisadas 
* @param    {Element} input O elemento input (this)
* @param    {String} prefix (opcional) Texto a ser inserido antes da string de pesquisa
* @param    {String} posfix (opcional) Texto a ser inserido apos da string de pesquisa
* @example  <input type="text" onkeyup="filterTable('main_table', [2, 3, 5, 6], this)">
*/
function filterTable(table_id, cols, input, prefix='', posfix=''){
  const table = document.getElementById(table_id);
  const filter = `${prefix}${input.value}${posfix}`.toLowerCase();
  let tr = table.tBodies[0].getElementsByTagName("tr");
  try {
    for (i = 0; i < tr.length; i++) {
      let row_value = '';
      for(j=0; j < cols.length;j++) {
        td = tr[i].getElementsByTagName("td")[cols[j]];
        row_value += td.textContent || td.innerText;
      }
      if (row_value.toLowerCase().indexOf(filter) > -1) {tr[i].style.display = "";}
      else {tr[i].style.display = "none";}
    }
  }catch(e){} 
}