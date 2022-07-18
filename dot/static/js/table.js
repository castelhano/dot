/*
* download_table_as_csv Retorna registros 'visiveis' da tabela em formato CSV
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
* sortTable Classifica os registros da tabela (vertical) ao clicar no cabecalho
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

// Adiciona listener para evento de click nos cabeçalhos de tabelas que contenham a classe table-sortable
document.querySelectorAll(".table-sortable th").forEach(headerCell => {
  headerCell.addEventListener("click", () => {
  const tableElement = headerCell.parentElement.parentElement.parentElement;
  const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
  const currentIsAscending = headerCell.classList.contains("th-sort-asc");  
  sortTable(tableElement, headerIndex, !currentIsAscending);
  });
});

/*
* filterTable Filtra linhas da tabela baseado no conteudo
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


/*
* paginate Implementa paginacao para dados de uma tabela
*
* @version  1.0
* @since    05/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Decricao abreviada do codigo
* @param    {Int} Parametro do codigo
* @returns  {Array} Retorno da funcao
* @throws   Excessoes lancadas pela funcao
* @example  Exemplo de utilizacao da funcao
* @see      {@link https://foo.com}
*/

// * VARIAVEIS ************************
var __paginateOn = false; __table = null, __rowsRaw = null, __rowsPerPage = null, __activePage = null, __paginateControl = null;
var __lastPage = null, __pagesClassList = null, __activePageClassList = null, __maxButtons = 6;
// ************************************

function paginate(table){
  let tbody = table.tBodies[0];
  let hbody = table.tBodies[1];
  let rows = Array.from(__rowsRaw);
  let pages = Math.ceil(rows.length / __rowsPerPage);
  __lastPage = pages;
  if(__activePage > __lastPage){__activePage = __lastPage}
  let feid = (__activePage - 1) * __rowsPerPage;
  let leid = Math.min((feid + __rowsPerPage) - 1, rows.length - 1);
  tbody.innerHTML = '';
  hbody.innerHTML = '';
  for(let i = 0;i < rows.length;i++){ // Divide os elementos nos tbody's
    if(i >= feid && i <= leid){tbody.appendChild(rows[i]);}
    else{hbody.appendChild(rows[i]);}
  }
// Montando os botoes das paginas
  __paginateControl.innerHTML = ''; // Limpa os botoem atuais
  // let startAt = Math.min(Math.max(1, __activePage - 1), (__lastPage - __maxButtons) + 1);
  let startAt = Math.max(Math.min(Math.max(1, __activePage - 1), (__lastPage - __maxButtons) + 1),1);
  let remmains = Math.min(__maxButtons, pages);
  for(let i = startAt; i <= __lastPage;i++){
    let btn = document.createElement('li');
    if(__activePage == i){btn.classList = __activePageClassList;}
    else{
      btn.classList = __pagesClassList;
      btn.setAttribute('onclick', `goToPage(${i})`);
    }
    btn.innerHTML = i;
    __paginateControl.appendChild(btn);
    remmains--;
    if(remmains == 1 && i < __lastPage){i = __lastPage -1}
    // else if(remmains == 1 && i < __lastPage)
  }
}
function paginateNextPage(){
  if(__activePage < __lastPage){
    __activePage++;
    paginate(__table);
  }
}

function paginatePreviousPage(){
  if(__activePage > 1){
    __activePage--;
    paginate(__table);
  }
}
function setRowsPerPage(qtde){__rowsPerPage = qtde;paginate(__table)}
function goToPage(page){__activePage = page;paginate(__table)}

function paginateTable(table_id, options){
  __paginateOn = true;
  let table = document.getElementById(table_id);
  __table = table;
  let mainControlContainer = options?.mainControlContainer || null;
  let paginateControlContainer = options?.paginateControlContainer || null;
  __rowsPerPage = options?.rowsPerPage || 10;
  __activePage = options?.activePage || 1;
  __rowsRaw = Array.from(table.querySelectorAll('tbody tr'));
  let mainControlClassList = options?.mainControlClassList || 'btn btn-sm btn-light border dropdown-toggle';
  let controlsClassList = options?.controlsClassList || 'paginate-page btn-secondary';
  __pagesClassList = options?.pagesClassList || 'paginate-page';
  __activePageClassList = options?.activePageClassList || 'paginate-page active';
  let tbody = table.querySelector('tbody'); // tbody da tabela, onde sera exibido 
  let hbody = document.createElement('tbody'); // tbody que sera adicionado na tabela para armazenar as rows ocultas
  hbody.classList = 'd-none'; 
  table.appendChild(hbody);
  let btnSetRowsPerPage = document.createElement('button');
  
  function buildMainControl(){
    let dp = document.createElement('div');
    let btn = document.createElement('button');
    let ul = document.createElement('ul');
    dp.classList = 'dropdown';
    btn.classList = mainControlClassList;
    btn.setAttribute('data-bs-toggle', 'dropdown');
    btn.innerHTML = 'Linhas ';
    ul.classList = 'dropdown-menu';
    let list = '<li class="dropdown-item pointer" onclick="setRowsPerPage(10)">10 registros</li>';
    list += '<li class="dropdown-item pointer" onclick="setRowsPerPage(30)">30 registros</li>';
    list += '<li class="dropdown-item pointer" onclick="setRowsPerPage(50)">50 registros</li>';
    list += '<li class="dropdown-item pointer" onclick="setRowsPerPage(__rowsRaw.length)">Todos</li>';
    ul.innerHTML = list;
    dp.appendChild(btn);
    dp.appendChild(ul);
    if(mainControlContainer){mainControlContainer.appendChild(dp)}
    else{
      let parent = table.parentElement;
      parent.insertBefore(dp, table);
    }
  }
  function buildPaginateControl(){
    let container = document.createElement('div');
    container.classList = 'text-end pe-2'
    let control = document.createElement('ul');
    control.classList = 'paginate-control';
    let first = document.createElement('li');
    first.onclick = () => goToPage(1);
    first.classList = controlsClassList;
    first.innerHTML = '<i class="fas fa-angle-double-left"></i>';
    let previous = document.createElement('li');
    previous.onclick = () => paginatePreviousPage();
    previous.classList = controlsClassList;
    previous.innerHTML = '<i class="fas fa-angle-left"></i>';
    let next = document.createElement('li');
    next.onclick = () => paginateNextPage();
    next.classList = controlsClassList;
    next.innerHTML = '<i class="fas fa-angle-right"></i>';
    __paginateControl = document.createElement('ul')
    __paginateControl.classList = 'paginate-control'
    control.appendChild(first);
    control.appendChild(previous);
    control.appendChild(next);
    
    container.appendChild(control);
    container.appendChild(__paginateControl);

    table.after(container);
  }
  buildMainControl();
  buildPaginateControl();
  paginate(table);
}