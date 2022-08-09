/*
* jsTable   Implementa operacoes com tabelas previamente criadas ou gera tabela a partir de dados json
*
* @version  2.6
* @since    07/08/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @doc      {@link ./md/jsTable.md}
* TODO:     Adicionar funcao GLOBAL jsTable_event()
*/
class jsTable{
    constructor(id, options){
        // Variaveis internas ********
        this.id = typeof id == 'string' ? id : id.id ? id.id : 'jsTable' ; // Armazena id da tabela (ou jsTable caso na informado id)
        this.table = typeof id == 'object' ? id : null; // Aponta para tabela alvo
        this.raw = []; // Guarda todos os TRs da tabela
        this.filteredRows = []; // Guarda as rows filtradas
        this.rawNextId = 0; // Armazena o proximo id disponivel, usado no medido addRow
        this.loadingEl = null; // Guarda o componente loading
        this.rowsCountLabel = null; // Span com a qtde de registros na tabela
        this.headers = []; // Arrays de strings com o nome dos headers da tabela
        this.thead = this.table ? this.table.tHead : null; // Aponta para thead
        this.tbody = this.table ? this.table.tBodies[0] : null; // Aponta para tbody principal (armazena registros visiveis)
        this.trash = []; // Ao deletar row, registro eh movido para o trash (permitndo retornar registro)
        this.pgControls = null; // Elemento UL que ira conter os botoes de navegacao da tabela
        this.lastPage = 0; // Armazena a ultima pagina da tabela
        this.leid = 0; // Last Element Id: Armazena o id do ultimo elemento a ser exibido no body (na pagina atual)
        this.restoreButton = null; // Armazena o botao para restaurar linha do trash, necessario para exibir e ocultar baseado na existencia de itens no trash
        this.exportBtn = null;
        this.filterInput = null;
        // Configuracao ********
        this.data = options?.data || []; // Json com dados para popular tabela
        this.container = options?.container || document.body; // parentNode da tabela, usado na construcao de tabela pelo evento createTable(), caso nao informado append nova tabela no body
        this.caption = options?.caption || null;
        this.canAddRow = options?.canAddRow != undefined ? options.canAddRow : false;
        this.canDeleteRow = options?.canDeleteRow != undefined ? options.canDeleteRow : false;
        this.canSave = options?.canSave != undefined ? options.canSave : false; // Boolean para exibicao do botao para salvar dados da tabela (funcao deve ser definida na origem)
        this.save = options?.save != undefined ? options.save : function(){console.log('jsTable: Nenhuma funcao definida para save, nas opcoes marque {canSave:true, save: suaFuncao} ')}; // Funcao definida aqui sera acionada no evento click do botao save
        this.canSort = options?.canSort != undefined ? options.canSort : true;
        this.canFilter = options?.canFilter != undefined ? options.canFilter : false;
        this.filterCols = options?.filterCols || []; // Recebe o nome das colunas a ser analisado ao filtar Ex: filterCols: ['nome', 'email']
        this.canExportCsv = options?.canExportCsv != undefined ? options.canExportCsv : true;
        this.csvSeparator = options?.csvSeparator || ';';
        this.csvClean = options?.csvClean != undefined ? options.csvClean : false; // Se setado para true remove acentuacao e caracteres especiais (normalize NFD)
        this.csvHeaders = options?.csvHeaders != undefined ? options.csvHeaders : true; // Define se sera incluido cabecalhos no arquivo de exportacao CSV
        this.canExportJson = options?.canExportJson != undefined ? options.canExportJson : false;
        this.editableCols = options?.editableCols || [];
        this.enablePaginate = options?.enablePaginate != undefined ? options.enablePaginate : false; // Booleno setado para true se paginacao estiver ativa para tabela
        this.pgControlContainer = options?.pgControlContainer || false; // Controles de paginacao por default criados logo abaixo da tabela, pode ser alterado setando esta variavel
        this.rowsPerPage = options?.rowsPerPage || 15; // Quantidade de registros a serem exibidos por pagina
        this.activePage = options?.activePage || 1; // Informa pagina exibida no momento (ou pode ser setada na criacao do objeto)
        this.maxPagesButtons = options?.maxPagesButtons || 6; // Quantidade maxima de botoes a serem exibidos 
        // Estilizacao ********
        this.tableClasslist = options?.tableClasslist || 'table border table-striped table-hover caption-top mb-2';
        this.editableColsClasslist = options?.editableColsClasslist || 'text-primary';
        this.rowsCountLabelClasslist = options?.rowsCountLabelClasslist || 'btn btn-sm btn-dark';
        this.addRowButtonClasslist = options?.addRowButtonClasslist || 'btn btn-sm btn-outline-success';
        this.addRowButtonText = options?.addRowButtonText || '<i class="fas fa-plus px-1"></i>';
        this.newRowClasslist = options?.newRowClasslist || 'table-success';
        this.deleteRowButtonClasslist = options?.deleteRowButtonClasslist || 'btn btn-sm btn-secondary';
        this.deleteRowButtonText = options?.deleteRowButtonText || '<i class="fas fa-trash"></i>';
        this.saveButtonClasslist = options?.saveButtonClasslist || 'btn btn-sm btn-outline-primary';
        this.saveButtonText = options?.saveButtonText || '<i class="fas fa-save px-1"></i>';
        this.restoreButtonClasslist = options?.restoreButtonClasslist || 'btn btn-sm btn-outline-secondary d-none';
        this.restoreButtonText = options?.restoreButtonText || '<i class="fas fa-history px-1"></i>';
        this.pgControlClasslist = options?.pgControlClasslist || 'pagination justify-content-end'; 
        this.pgPageClasslist = options?.pgPageClasslist || 'page-item';
        this.pgLinkClasslist = options?.pgLinkClasslist || 'page-link';
        this.pgFirstButtonLabel = options?.pgFirstButtonLabel || '<i class="fas fa-angle-double-left"></i>';
        this.pgPreviousButtonLabel = options?.pgPreviousButtonLabel || '<i class="fas fa-angle-left"></i>';
        this.pgNextButtonLabel = options?.pgNextButtonLabel || '<i class="fas fa-angle-right"></i>';
        this.emptyTableMessage = options?.emptyTableMessage || 'Nenhum registro a exibir';
        if(this.table == null){
            this.createTable();
            this.buildHeaders();
            this.buildControls();
            this.buildRows();
            this.buildListeners();
        }
        else{
            this.validateTable();
            this.buildControls();
            this.buildListeners();
        }
        if(this.enablePaginate){this.paginate();}
        this.loading(true); // Oculta sppiner de loading quando terminado de carregar tabela
    }
    createTable(){
        this.table = document.createElement('table');
        this.table.id = this.id;
        this.table.classList = this.tableClasslist;
        this.thead = document.createElement('thead');
        this.tbody = document.createElement('tbody');
        this.table.caption = document.createElement('caption');
        this.table.caption.style.position = 'relative';
        this.table.appendChild(this.thead);
        this.table.appendChild(this.tbody);
        this.container.appendChild(this.table);
    }
    buildHeaders(){
        let tr = document.createElement('tr');
        for(let i = 0;i < this.data.length;i++){
            for(let j in this.data[i]){
                if(!this.headers.includes(j)){
                    this.headers.push(j);
                    let th = document.createElement('th');
                    th.setAttribute('data-key',j);
                    th.innerHTML = j[0].toUpperCase() + j.substring(1);
                    if(this.canFilter && this.filterCols.includes(j)){th.innerHTML += '*'}
                    tr.appendChild(th);
                }
            }
        }
        if(this.canDeleteRow){ // Caso habilitado deleteRow, adiciona uma th relativa ao controle
            let th = document.createElement('th');
            th.innerHTML = '';
            tr.appendChild(th);
        }
        this.thead.appendChild(tr);
    }
    buildRows(){
        this.cleanRows();
        let data_size = this.data.length;
        this.rawNextId = data_size + 1; // Ajusta o id de um eventual proximo elemento a ser inserido
        for(let i = 0;i < data_size;i++){
            let row = document.createElement('tr');
            row.dataset.rawRef = i;
            for(let j = 0;j < this.headers.length;j++){
                let v = this.data[i][this.headers[j]]; // Busca no json data se existe valor na row para o header, retorna o valor ou undefinied (caso nao encontre)
                let col = document.createElement('td');
                col.innerHTML = v != undefined ? v : ''; // Insere valor ou empty string '' para o campo
                let editable = this.editableCols.includes(this.headers[j]);
                col.contentEditable = editable ? true : false; // Verifica se campo pode ser editado, se sim marca contentEditable='True'
                col.classList = editable ? this.editableColsClasslist : ''; // Se campo for editavel, acidiona classe definida em editableColsClasslist
                row.appendChild(col);
            }
            this.rowAddControls(row); // Adiciona controles para row
            this.tbody.appendChild(row); // Insere row na tabela
            this.raw.push(row); 
        }
        if(data_size == 0){this.addEmptyRow();} // Caso nao exista nenhum registro, adiciona linha vazia
        this.rowsCountLabel.innerHTML = data_size;
    }
    rowAddControls(row){
        if(this.canDeleteRow){
            let controls = document.createElement('td');
            controls.classList = 'text-end py-1';
            let deleteBtn = document.createElement('span');
            deleteBtn.classList = this.deleteRowButtonClasslist;
            deleteBtn.innerHTML = this.deleteRowButtonText;
            deleteBtn.onclick = () => this.deleteRow(row);
            controls.appendChild(deleteBtn);
            row.appendChild(controls);
        }
    }
    buildControls(){
        this.table.classList.add('caption-top'); // Adiciona a classe caption top (caso nao exista)
        if(this.canSort){this.table.classList.add('table-sortable')}
        if(this.enablePaginate){ // Cria os controles gerais para paginacao (first, next e previous)
            let pgNav = this.pgControlContainer || document.createElement('nav'); // Container principal dos controles de navegacao da tabela
            this.pgControls = document.createElement('ul'); // Controles de navegacao
            this.pgControls.classList = this.pgControlClasslist;
            let first = document.createElement('li');
            first.onclick = () => this.goToPage(1);
            first.classList = this.pgPageClasslist;
            first.innerHTML = `<span class="${this.pgLinkClasslist}">${this.pgFirstButtonLabel}</span>`;
            let previous = document.createElement('li');
            previous.onclick = () => this.previousPage();
            previous.classList = this.pgPageClasslist;
            previous.innerHTML = `<span class="${this.pgLinkClasslist}">${this.pgPreviousButtonLabel}</span>`;
            let next = document.createElement('li');
            next.onclick = () => this.nextPage();
            next.classList = this.pgPageClasslist;
            next.innerHTML = `<span class="${this.pgLinkClasslist}">${this.pgNextButtonLabel}</span>`;
            this.pgControls.appendChild(first); // Adiciona o botao para primeira pagina no pgControls
            this.pgControls.appendChild(previous); // Adiciona o botao para pagina anterior no pgControls
            this.pgControls.appendChild(next); // Adiciona o botao para proxima pagina no pgControls
            pgNav.appendChild(this.pgControls); // Adiciona o pgControls no container de navegacao
            if(!this.pgControlContainer){this.table.after(pgNav);} // Insere nav (caso nao definido container na instancia da clsse) com controles de paginacao no fim da tabela
        }
        // Controles do caption (filter input, addRow, export, save etc...)
        let capRow = document.createElement('div');capRow.classList = 'row g-2'; // Inicia row
        if(this.caption){ // Se informado caption ao instanciar objeto, cria div.col com conteudo do caption
            let capText = document.createElement('div');
            capText.classList = 'col-auto pe-2';
            capText.innerHTML = this.caption;
            capRow.appendChild(capText);
        }
        if(this.canFilter){ // Se habilitado filtro insere div.col com input.text para filtrar tabela
            let capFilter = document.createElement('div');
            capFilter.classList = 'col';
            this.filterInput = document.createElement('input');
            this.filterInput.type = 'text';
            this.filterInput.disabled = this.filterCols.length > 0 ? false : true;
            this.filterInput.classList = 'form-control form-control-sm';
            this.filterInput.placeholder = 'Filtrar*';
            this.filterInput.onkeyup = () => this.filter();
            capFilter.appendChild(this.filterInput);
            capRow.appendChild(capFilter);
        }
        let capControlsGroup = document.createElement('div'); // Inicia btn-group
        capControlsGroup.classList = 'btn-group';
        this.rowsCountLabel = document.createElement('button'); // Cria elemento que vai armazenar a quantidade de registros na tabela
        this.rowsCountLabel.classList = this.rowsCountLabelClasslist;
        this.rowsCountLabel.disabled = true;
        this.rowsCountLabel.innerHTML = this.raw.length;
        capControlsGroup.appendChild(this.rowsCountLabel);
        if(this.canAddRow){
            let btn = document.createElement('button');
            btn.classList = this.addRowButtonClasslist;
            btn.onclick = () => this.addRow();
            btn.innerHTML = this.addRowButtonText;
            capControlsGroup.appendChild(btn);
        }
        if(this.canSave){
            let btn = document.createElement('button');
            btn.classList = this.saveButtonClasslist;
            btn.onclick = () => this.save();
            btn.innerHTML = this.saveButtonText;
            capControlsGroup.appendChild(btn);
        }
        if(this.canDeleteRow){
            this.restoreButton = document.createElement('button');
            this.restoreButton.classList = this.restoreButtonClasslist;
            this.restoreButton.onclick = () => this.restoreRow();
            this.restoreButton.innerHTML = this.restoreButtonText;
            capControlsGroup.appendChild(this.restoreButton);
        }
        if(this.canExportCsv){
            let btn = document.createElement('button');
            btn.classList = 'btn btn-sm btn-outline-secondary';
            btn.onclick = () => this.exportCsv();
            btn.innerHTML = 'CSV';
            capControlsGroup.appendChild(btn);
        }
        if(this.canExportJson){
            let btn = document.createElement('button');
            btn.classList = 'btn btn-sm btn-outline-secondary';
            btn.onclick = (e) => this.exportJson(e);
            btn.innerHTML = 'JSON';
            capControlsGroup.appendChild(btn);
        }
        let capControls = document.createElement('div');
        capControls.classList = 'col-auto ms-auto';
        capControls.appendChild(capControlsGroup);
        capRow.appendChild(capControls);
        this.table.caption.appendChild(capRow);
        this.loadingEl = document.createElement('div');
        this.loadingEl.classList = 'text-center bg-light position-absolute border w-100 top-0 py-2';
        this.loadingEl.innerHTML = '<div class="spinner-border text-success fs-7" role="status"><span class="visually-hidden">Loading...</span></div>';
        this.table.caption.appendChild(this.loadingEl); // Adiciona loading componente na tabela        
    }
    buildListeners(){
        if(this.canSort){
            this.thead.querySelectorAll("th").forEach(headerCell => {
                headerCell.addEventListener("click", () => {
                    const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
                    const currentIsAscending = headerCell.classList.contains("th-sort-asc");  
                    this.sort(headerIndex, !currentIsAscending);
                });
            });
        }
    }
    loadData(json){ // Carrega dados na tabela (!! Limpa dados atuais)
        this.loading(); // Mostra spinner de carregamento
        this.data = json;
        this.cleanTable();
        this.buildHeaders();
        this.buildListeners();
        this.buildRows();
        if(this.enablePaginate){this.paginate()}
        this.loading(true); // Oculta spinner de carregamento
    }
    appendData(json){ // Carrega dados na tabela (mantem dados atuais) (!! Não adiciona novos cabecalhos)
        let data_size = json.length;
        let first = this.rawNextId; // Inicio dos ids a serem inseridos
        let last = first + data_size; // Ultimo id a ser inserido
        for(let i = 0; i < data_size;i++){
            let row = document.createElement('tr');
            row.dataset.rawRef = first + i;
            for(let j = 0;j < this.headers.length;j++){
                let v = json[i][this.headers[j]]; // Busca no json data se existe valor na row para o header, retorna o valor ou undefinied (caso nao encontre)
                let col = document.createElement('td');
                col.innerHTML = v != undefined ? v : ''; // Insere valor ou empty string '' para o campo
                let editable = this.editableCols.includes(this.headers[j]);
                col.contentEditable = editable ? true : false; // Verifica se campo pode ser editado, se sim marca contentEditable='True'
                col.classList = editable ? this.editableColsClasslist : ''; // Se campo for editavel, acidiona classe definida em editableColsClasslist
                row.appendChild(col);
            }
            this.rowAddControls(row); // Adiciona controles para row
            this.raw.push(row);
            if(this.enablePaginate){this.paginate()} // Se habilado paginacao, refaz paginacao
            else{this.tbody.appendChild(row);} // Caso contrario so insere row na tabela
        }
        this.rowsCountLabel.innerHTML = this.raw.length;
        // this.raw = this.raw.concat(json);
        // if(this.enablePaginate){this.paginate()}
    }
    filter(criterio=null){
        if(this.raw.length == 0){ return null } // Se tabela for fazia, nao executa processo para filtro
        let c = criterio || this.filterInput.value.toLowerCase();
        if(this.canFilter && this.filterCols.length > 0 && c != ""){
            this.filteredRows = []; // Limpa os filtros
            let rows_size = this.raw.length;
            let cols_size = this.headers.length;
            let cols = []; // Array armazena os indices das coluas a serem analizadas
            for(let i = 0;i < cols_size;i++){ // Monta array com indices das colunas procuradas
                if(this.filterCols.includes(this.headers[i])){cols.push(i)}
            }
            let row_count = 0;
            for (let i = 0; i < rows_size; i++) { // Percorre todas as linhas, e verifica nas colunas definidas em filterCols, se texto atende criterio
                let row_value = '';
                for(let j=0; j < cols.length;j++) {
                    try{ // Caso exista celulas mescladas cols[j] sera null, try omite apresentacao de erro
                        let td = this.raw[i].getElementsByTagName("td")[cols[j]];
                        row_value += td.textContent || td.innerText;
                    }catch(e){}
                }
                if(row_value.toLowerCase().indexOf(c) > -1) {this.filteredRows.push(this.raw[i]);row_count++;}
            }            
            if(row_count == 0){
                let tr = document.createElement('tr');
                tr.innerHTML = `<td colspan="${this.canDeleteRow ? this.headers.length + 1 : this.headers.length}">Nenhum registro encontrado com o criterio informado</td>`;
                this.filteredRows.push(tr);
            }
            this.rowsCountLabel.innerHTML = row_count;
        }
        else if(c == ""){
            this.filteredRows = [];
            this.rowsCountLabel.innerHTML = this.raw.length

        }; // Ao limpar filtro, limpa array com rows filtradas
        if(this.enablePaginate){this.paginate()} // Refaz paginacao
        else{ // Caso paginacao nao esteja ativa, limpa as rows da tabela e carrega (filteredRows ou raw)
            this.cleanRows();
            if(this.filteredRows.length > 0){this.filteredRows.forEach((r) => this.tbody.append(r))}
            else{
                if(this.raw.length > 0){this.raw.forEach((r) => this.tbody.append(r));}
                else{this.addEmptyRow();} // Caso nao exista nenhum registro, mostra linha com mensagem
            }
        }
    }
    paginate(){
        if(!this.enablePaginate){this.enablePaginate = true;} // Caso metodo seja acionado apos objeto instanciado, ativa flag enablePaginate = true
        let data = this.filteredRows.length > 0 ? this.filteredRows : this.raw; // Faz paginamento pelo array raw ou filteredRows (caso registros filtrados)
        let rowsSize = data.length;
        if(rowsSize > 0){
            this.lastPage = Math.ceil(rowsSize / this.rowsPerPage);
            if(this.activePage > this.lastPage){this.activePage = this.lastPage} // Impede tentativa de acesso de pagina maior que a qtde de paginas
            if(this.activePage < 1){this.activePage = 1} // Impede tentativa de acesso de pagina menor que 1
            let feid = (this.activePage - 1) * this.rowsPerPage; // FirstElementId: Seta o ID do primeiro elemento a ser mostrado
            this.leid = Math.min((feid + this.rowsPerPage) - 1, rowsSize - 1); // LastElementId: Seta o ID do ultimo elemento a ser mostrado   
            this.cleanRows();
            for(let i = feid;i <= this.leid;i++ ){
                this.tbody.appendChild(data[i]);
            }
        }
        else{this.lastPage = 1; this.activePage = 1;} // Se tabela vazia, cria uma unica pagina e aponta p ela
        this.pgBuildPageControls(this.lastPage);
    }
    pgBuildPageControls(pages){ // Cria botoes de navegacao das paginas
        let btns = this.pgControls.querySelectorAll('[data-type="pgPage"]'); // Seleciona todos os botoes de paginas
        btns.forEach(btn => {btn.remove();}); // Remove todos os botoes
        let startAt = Math.max(Math.min(Math.max(1, this.activePage - 1), (pages - this.maxPagesButtons) + 1),1); // Primeira pagina a ser exibida
        let current = startAt; // Contador para iteracao nas paginas
        let remmains = Math.min(this.maxPagesButtons, pages); // Contador para qtde de paginas restantes a inserir
        while(remmains > 0){ // Insere um botao para cada pagina (maximo definido em this.maxPagesButtons)
            let btn = document.createElement('li');
            btn.classList = this.pgPageClasslist;
            btn.dataset.type = 'pgPage';
            btn.dataset.page = current;
            if(this.activePage == current){btn.classList.add('active');}
            else{
                btn.onclick = () => this.goToPage(btn.dataset.page);
            } // Caso nao seja botao referente a pagina atual, adiciona trigger para pagina correspondente
            btn.innerHTML = `<a class="${this.pgLinkClasslist}">${current}</a>`;
            this.pgControls.appendChild(btn);
            current++;remmains--;
            if(remmains == 1){current = pages} // Ultimo botao sempre aponta para ultima pagina
        }
    }
    sort(column, asc=true){
        if(this.raw.length == 0){ return null } // Se tabela for fazia, nao executa processo para classificar
        const modifier = asc ? 1 : -1; // Modificador para classificar em order crecente (asc=true) ou decrescente (asc=false)
        let rows = this.filteredRows.length > 0 ? this.filteredRows : this.raw; // Busca linhas em this.filteredRows (caso filtrado) ou em this.raw caso nao
        const sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
            const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();  
            return aColText > bColText ? (1 * modifier) : (-1 * modifier);
        });
        // this.cleanRows(); // Limpa rows da tabela
        rows = sortedRows; // Atualiza campos (filteredRows ou no raw)
        if(this.enablePaginate){this.paginate()} // Se paginacao habilitada, refaz paginacao
        else{rows.forEach((e) => this.tbody.append(e))} // Caso nao, atualiza o tbody da tabela
        
        this.thead.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
        this.thead.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
        this.thead.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);
    }
    goToPage(page){this.activePage = page;this.paginate();}
    previousPage(){this.activePage--;this.paginate();}
    nextPage(){this.activePage++;this.paginate();}
    addRow(){ // Adiciona nova linha na tabela
        if(this.raw.length == 0){this.tbody.querySelector('[data-type="emptyRow"]').remove();} // Se tabela vazia, remove linha de emptyRow
        if(this.enablePaginate){this.goToPage(this.lastPage)}; // Muda exibicao para ultima pagina
        let tr = document.createElement('tr');
        tr.dataset.rawRef = this.rawNextId;
        tr.classList = this.newRowClasslist;
        for(let i = 0;i < this.headers.length;i++){
            let td = document.createElement('td');
            td.innerHTML = ''
            td.contentEditable = true; // Na nova linha todos os campos sao editaveis
            td.classList = this.editableColsClasslist;
            tr.appendChild(td);
        }
        this.rowAddControls(tr);
        this.raw.push(tr);
        this.tbody.appendChild(tr);
        this.rawNextId++; // Incrementa o rawNextId para eventual proximo elemento a ser inserido
        this.rowsCountLabel.innerHTML = this.raw.length; // Ajusta contador para tabela
    }
    deleteRow(row){
        let done = false;
        let i = 0;
        let max = this.raw.length;
        while(!done && i <= max){ // Percorre o raw buscando a linha a ser removida
            if(this.raw[i].dataset.rawRef == row.dataset.rawRef){
                this.trash.push(this.raw.splice(i,1)[0]); // Remove elemento do raw e insere no trash
                done = true;
            }
            i++;
        }
        row.remove(); // Remove o elemento da tabela
        this.rowsCountLabel.innerHTML = this.raw.length; // Ajusta contador para tabela
        if(this.raw.length == 0){this.addEmptyRow()} // Se linha excluida for a unica da tabela, adiciona emptyRow
        if(this.enablePaginate){
            try {this.tbody.appendChild(this.raw[this.leid]);}catch(error){} // Adiciona (se existir) proximo elemento ao final do tbody
            this.paginate(); // Refaz paginacao
        }
        this.restoreButton.classList.remove('d-none'); // Exibe botao para restaurar linha
    }
    restoreRow(){
        let tr = this.trash.pop();
        tr.classList = 'table-warning';
        if(this.enablePaginate){this.goToPage(this.lastPage)};
        this.tbody.appendChild(tr);
        this.raw.push(tr);
        if(this.trash.length == 0){this.restoreButton.classList.add('d-none');}
        this.rowsCountLabel.innerHTML = this.raw.length; // Ajusta contador para tabela
    }
    getRows(){ // Retorna array com todas as linhas da tabela
        let items = [];
        let raw_size = this.raw.length;
        for(let i = 0;i < raw_size;i++){
            let item = {};
            let cols = this.raw[i].querySelectorAll('td');
            let cols_size = this.canDeleteRow ? cols.length - 1 : cols.length; // cols.length - 1 desconsidera a ultima coluna dos controles
            for(let j = 0; j < cols_size; j++){ 
                item[this.headers[j]] = cols[j].innerText.replace('\n', '');
            }
            items[i] = item;
        }
        return items;
    }
    getJson(){return JSON.stringify(this.getRows())} // Retorna todas as linhas da tabela em formato Json
    exportJson(e){
        let data = this.getJson();
        let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(data);
        let filename = `${this.id}.json`;
        let btn = document.createElement('a');
        btn.classList = 'd-none';
        btn.setAttribute('href', dataUri);
        btn.setAttribute('download', filename);
        btn.click();
        btn.remove();
        let originalClasslist = e.target.classList.value;
        let originalHtml = e.target.innerHTML;
        e.target.classList = 'btn btn-sm btn-success';
        try {dotAlert('success', 'Arquivo baixado com sucesso')}catch(error){}
        setTimeout(function() {e.target.classList = originalClasslist;}, 800);
    }
    exportCsv(){
        let csv = [];
        let raw_size = this.raw.length;
        if(this.csvHeaders){ // Insere cabecalhos
            csv.push(this.headers.join(this.csvSeparator));
        }
        for (let i = 0; i < raw_size; i++) {
            let row = [], cols = this.raw[i].querySelectorAll('td, th');
            let cols_size = this.canDeleteRow ? cols.length - 1 : cols.length; // Desconsidera coluna de controles (se existir)
            for (let j = 0; j < cols_size; j++) {
                let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' '); // Remove espacos multiplos e quebra de linha
                if(this.csvClean){data = data.normalize("NFD").replace(/[\u0300-\u036f]/g, "");} // Remove acentuação e caracteres especiais
                data = data.replace(/"/g, '""'); // Escape double-quote com double-double-quote 
                row.push('"' + data + '"'); // Carrega string
            }
            csv.push(row.join(this.csvSeparator));
        }
        let csv_string = csv.join('\n');
        let filename = `${this.id}.csv`;
        let link = document.createElement('a');
        link.style.display = 'none';
        link.setAttribute('target', '_blank');
        link.setAttribute('href', 'data:text/csv;charset=utf-8,%EF%BB%BF' + encodeURIComponent(csv_string));
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
    }
    cleanTable(){this.thead.innerHTML = '';this.tbody.innerHTML = '';}
    cleanRows(){this.tbody.innerHTML = '';}
    addEmptyRow(){this.tbody.innerHTML = `<td data-type="emptyRow" colspan="${this.headers.length}">${this.emptyTableMessage}</td>`;}
    removeEmptyRow(){}
    loading(done=false){
        if(done){this.loadingEl.classList.add('d-none')}
        else{this.loadingEl.classList.remove('d-none')}
    }
    validateTable(){ // Metodo chamado em tabelas previamente criadas, normaliza e categoriza elementos  
        if(!this.table.caption){this.table.caption = document.createElement('caption');} // Cria o caption da tabela caso nao exista
        else{this.caption = this.table.caption.innerHTML;this.table.caption.innerHTML = ''} // Limpa o caption atual, sera refeito no metodo buildControls
        let ths = this.table.tHead.querySelectorAll('th,td'); // Busca todos os elementos th ou td no header da tabela
        for(let i = 0; i < ths.length;i++){ // Percorre todos os headers, ajustando conteudo e populando array de headers
            ths[i].setAttribute('data-key',ths[i].innerText); // Ajusta o data-attr key com o valor informado no th
            this.headers.push(ths[i].innerText); // Adiciona o header no array de headers
            if(this.canFilter && this.filterCols.includes(ths[i].innerText)){ths[i].innerHTML += '*'} // Verifica se header esta marcado para ser filtrado, se sim adiciona caracter identificador
            
        }
        
        let trs = this.table.querySelectorAll('tbody tr'); // Busca todas as linhas dentro de um tbody
        let trs_count = trs.length;
        this.rawNextId = trs_count; // Ajusta o id de um eventual proximo elemento a ser inserido
        for(let i = 0; i < trs_count; i++){
            trs[i].dataset.rawRef = i; // Ajusta data-attr rawRef do elemento tr
            let cols_size = trs[i].querySelectorAll('td').length;
            for(let j = 0; j < cols_size; j++){ // Percorre todas as colunas da tr para setar contentEditable nas colunas definidas em this.editableCols
                let editable = this.editableCols.includes(ths[j].dataset.key);
                trs[i].querySelectorAll('td')[j].contentEditable = editable ? true : false; // Verifica se campo pode ser editado, se sim marca contentEditable='True'
                let originalClasslist = trs[i].querySelectorAll('td')[j].className;
                trs[i].querySelectorAll('td')[j].classList = editable ? originalClasslist + this.editableColsClasslist : originalClasslist; // Se campo for editavel, acidiona classe definida em editableColsClasslist
            }
            this.rowAddControls(trs[i]); // Adiciona controles para row
            this.raw.push(trs[i]); // Adiciona linha no array raw
        }
        if(trs_count == 0){this.addEmptyRow();} // Caso nao exista nenhum registro, adiciona linha vazia
    }
}