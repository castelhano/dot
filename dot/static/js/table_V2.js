
// TODO:
// adicionar campo para delete row (headers e rows) em tabela criada previamente

class jsTable{
    constructor(id, options){
        this.id = typeof id == 'string' ? id : id.id; // Armazena id da tabela
        this.table = typeof id == 'object' ? id : null; // Aponta para tabela alvo
        this.data = options?.data || []; // Json com dados para popular tabela
        this.raw = []; // Guarda todos os TRs da tabela
        this.rawNextId = 0; // Armazena o proximo id disponivel, usado no medido addRow
        this.caption = options?.caption || null;
        this.headers = []; // Arrays de strings com o nome dos headers da tabela
        this.thead = this.table ? this.table.tHead : null; // Aponta para thead
        this.tbody = this.table ? this.table.tBodies[0] : null; // Aponta para tbody principal (armazena registros visiveis)
        this.trash = []; // Ao deletar row, registro eh movido para o trash (permitndo retornar registro)
        this.tableClasslist = options?.tableClasslist || 'table border table-striped table-hover caption-top mb-2';
        this.editableColsClasslist = options?.editableColsClasslist || 'text-primary';
        this.container = options?.container || document.body; // parentNode da tabela, usado na construcao de tabela pelo evento createTable(), caso nao informado append nova tabela no body
        this.editableCols = options?.editableCols || [];
        this.enablePaginate = options?.enablePaginate != undefined ? options.enablePaginate : false; // Booleno setado para true se paginacao estiver ativa para tabela
        this.pgControlContainer = options?.pgControlContainer || false; // Controles de paginacao por default criados logo abaixo da tabela, pode ser alterado setando esta variavel
        this.pgControls = null; // Elemento UL que ira conter os botoes de navegacao da tabela
        this.rowsPerPage = options?.rowsPerPage || 15; // Quantidade de registros a serem exibidos por pagina
        this.activePage = options?.activePage || 1; // Informa pagina exibida no momento (ou pode ser setada na criacao do objeto)
        this.lastPage = 0; // Armazena a ultima pagina da tabela
        this.maxPagesButtons = options?.maxPagesButtons || 6; // Quantidade maxima de botoes a serem exibidos 
        this.leid = 0;
        this.pgControlClasslist = options?.pgControlsClasslist || 'pagination justify-content-end'; 
        this.pgPageClasslist = options?.pgPageClasslist || 'page-item';
        this.pgLinkClasslist = options?.pgLinkClasslist || 'page-link';
        this.pgFirstLabel = options?.pgFirstLabel || '<i class="fas fa-angle-double-left"></i>';
        this.pgPreviousLabel = options?.pgPreviousLabel || '<i class="fas fa-angle-left"></i>';
        this.pgNextLabel = options?.pgNextLabel || '<i class="fas fa-angle-right"></i>';
        this.canAddRow = options?.canAddRow != undefined ? options.canAddRow : false;
        this.newRowClasslist = options?.newRowClasslist || 'table-success';
        this.canSave = options?.canSave != undefined ? options.canSave : false; // Boolean para exibicao do botao para salvar dados da tabela (funcao deve ser definida na origem)
        this.save = options?.save != undefined ? options.save : function(){console.log('jsTable: Nenhuma funcao definida para save, nas opcoes marque {canSave:true, save: suaFuncao()} ')}; // Funcao definida aqui sera acionada no evento click do botao save
        this.canDeleteRow = options?.canDeleteRow != undefined ? options.canDeleteRow : false;
        this.deleteRowClasslist = options?.deleteRowClasslist || 'btn btn-sm btn-secondary';
        this.deleteRowText = options?.deleteRowText || '<i class="fas fa-trash"></i>';
        this.canExportCsv = options?.canExportCsv != undefined ? options.canExportCsv : true;
        this.csvSeparator = options?.csvSeparator || ';';
        this.csvClean = options?.csvClean != undefined ? options.csvClean : false; // Se setado para true remove acentuacao e caracteres especiais (normalize NFD)
        this.canExportJson = options?.canExportJson != undefined ? options.canExportJson : true;
        this.exportBtn = null;
        this.canFilter = options?.canFilter != undefined ? options.canFilter : false;
        this.filterInput = null;
        this.filterCols = options?.filterCols || []; // Recebe o nome das colunas a ser analisado ao filtar Ex: filterCols: ['nome', 'email']
        this.canSort = options?.canSort != undefined ? options.canSort : false;
        if(this.table == null){
            this.createTable();
            this.buildHeaders();
            this.buildRows();
        }
        else{this.validateTable()}
        this.buildControls();
        // this.buildListeners();
        if(this.enablePaginate){this.paginate()}
    }
    createTable(){
        this.table = document.createElement('table');
        this.table.id = this.id;
        this.table.classList = this.tableClasslist;
        this.thead = document.createElement('thead');
        this.tbody = document.createElement('tbody');
        this.table.caption = document.createElement('caption');
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
    }
    rowAddControls(row){
        if(this.canDeleteRow){
            let controls = document.createElement('td');
            controls.classList = 'text-end py-1';
            let deleteBtn = document.createElement('span');
            deleteBtn.classList = this.deleteRowClasslist;
            deleteBtn.innerHTML = this.deleteRowText;
            deleteBtn.onclick = () => this.deleteRow(row);
            controls.appendChild(deleteBtn);
            row.appendChild(controls);
        }
    }
    buildControls(){
        if(this.canSort){this.table.classList.add('table-sortable')}
        if(this.enablePaginate){ // Cria os controles gerais para paginacao (first, next e previous)
            let pgNav = this.pgControlContainer || document.createElement('nav'); // Container principal dos controles de navegacao da tabela
            this.pgControls = document.createElement('ul'); // Controles de navegacao
            this.pgControls.classList = this.pgControlClasslist;
            let first = document.createElement('li');
            first.onclick = () => this.goToPage(1);
            first.classList = this.pgPageClasslist;
            first.innerHTML = `<span class="${this.pgLinkClasslist}">${this.pgFirstLabel}</span>`;
            let previous = document.createElement('li');
            previous.onclick = () => this.previousPage();
            previous.classList = this.pgPageClasslist;
            previous.innerHTML = `<span class="${this.pgLinkClasslist}">${this.pgPreviousLabel}</span>`;
            let next = document.createElement('li');
            next.onclick = () => this.nextPage();
            next.classList = this.pgPageClasslist;
            next.innerHTML = `<span class="${this.pgLinkClasslist}">${this.pgNextLabel}</span>`;
            this.pgControls.appendChild(first); // Adiciona o botao para primeira pagina no pgControls
            this.pgControls.appendChild(previous); // Adiciona o botao para pagina anterior no pgControls
            this.pgControls.appendChild(next); // Adiciona o botao para proxima pagina no pgControls
            pgNav.appendChild(this.pgControls); // Adiciona o pgControls no container de navegacao
            if(!this.pgControlContainer){this.table.after(pgNav);} // Insere nav (caso nao definido container na instancia da clsse) com controles de paginacao no fim da tabela
        }
        // Controles do caption (filter input, addRow, export, save etc...)
        let capRow = document.createElement('div');capRow.classList = 'row g-2';
        if(this.caption){
            let capText = document.createElement('div');
            capText.classList = 'col-auto pe-2';
            capText.innerHTML = this.caption;
            capRow.appendChild(capText);
        }
        if(this.canFilter){
            let capFilter = document.createElement('div');
            capFilter.classList = 'col';
            this.filterInput = document.createElement('input');
            this.filterInput.type = 'text';
            this.filterInput.classList = 'form-control form-control-sm';
            this.filterInput.placeholder = 'Filtrar*';
            this.filterInput.onkeyup = () => this.filter();
            capFilter.appendChild(this.filterInput);
            capRow.appendChild(capFilter);
        }
        let capControlsGroup = document.createElement('div');
        capControlsGroup.classList = 'btn-group';
        if(this.canAddRow){
            let btn = document.createElement('button');
            btn.classList = 'btn btn-sm btn-outline-success';
            btn.onclick = () => this.addRow();
            btn.innerHTML = '<i class="fas fa-plus px-1"></i>';
            capControlsGroup.appendChild(btn);
        }
        if(this.canSave){
            let btn = document.createElement('button');
            btn.classList = 'btn btn-sm btn-outline-primary';
            btn.onclick = () => this.save();
            btn.innerHTML = '<i class="fas fa-save px-1"></i>';
            capControlsGroup.appendChild(btn);
        }
        if(this.canDeleteRow){
            let btn = document.createElement('button');
            btn.id = 'jsTableRestoreRow';
            btn.classList = 'btn btn-sm btn-outline-secondary d-none';
            btn.onclick = () => this.restoreRow();
            btn.innerHTML = '<i class="fas fa-history px-1"></i>';
            capControlsGroup.appendChild(btn);
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
    }
    buildListeners(){
    }
    setEditableCols(){} // Somente usado em tabelas previamente criadas
    loadData(json){ // Carrega dados na tabela (!! Limpa dados atuais)
        this.data = json;
        this.cleanTable();
        this.buildHeaders();
        this.buildRows();
    }
    appendRows(json){} // Carrega dados na tabela (mantem dados atuais) (!! Não adiciona novos cabecalhos)
    filter(criterio=null){
        if(this.canFilter){
            let c = criterio || this.filterInput.value.toLowerCase();
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
                    let td = this.raw[i].getElementsByTagName("td")[cols[j]];
                    row_value += td.textContent || td.innerText;
                }
                if (row_value.toLowerCase().indexOf(c) > -1) {this.raw[i].style.display = ": table-row";row_count++;}
                else {this.raw[i].style.display = "none";}
            }
            if(row_count == 0){
                this.tbody.innerHTML = `<tr><td colspan="${this.canDeleteRow ? this.headers.length + 1 : this.headers.length}">Nenhum registro encontrado com o criterio informado</td></tr>`;
            }
            
        }
    }
    paginate(){
        let rowsSize = this.raw.length;
        this.lastPage = Math.ceil(rowsSize / this.rowsPerPage);
        if(this.activePage > this.lastPage){this.activePage = this.lastPage} // Impede tentativa de acesso de pagina maior que a qtde de paginas
        if(this.activePage < 1){this.activePage = 1} // Impede tentativa de acesso de pagina menor que 1
        let feid = (this.activePage - 1) * this.rowsPerPage; // FirstElementId: Seta o ID do primeiro elemento a ser mostrado
        this.leid = Math.min((feid + this.rowsPerPage) - 1, rowsSize - 1); // LastElementId: Seta o ID do ultimo elemento a ser mostrado   
        this.tbody.innerHTML = ''; // Limpa os tbody principal
        for(let i = feid;i <= this.leid;i++ ){
            this.tbody.appendChild(this.raw[i]);
        }
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
    goToPage(page){this.activePage = page;this.paginate();}
    previousPage(){this.activePage--;this.paginate();}
    nextPage(){this.activePage++;this.paginate();}
    addRow(){ // Adiciona nova linha na tabela
        if(this.enablePaginate){this.goToPage(this.lastPage)}; // Muda exibicao para ultima pagina
        let tr = document.createElement('tr');
        tr.dataset.rawRef = this.rawNextId;
        tr.classList = this.newRowClasslist;
        for(let i = 0;i < this.headers.length;i++){
            let td = document.createElement('td');
            td.innerHTML = '&nbsp;'
            td.contentEditable = true; // Na nova linha todos os campos sao editaveis
            td.classList = this.editableColsClasslist;
            tr.appendChild(td);
        }
        this.rowAddControls(tr);
        this.raw.push(tr);
        this.tbody.appendChild(tr);
        this.rawNextId++; // Incrementa o rawNextId para eventual proximo elemento a ser inserido
    }
    deleteRow(row){
        let done = false;
        let i = 0;
        let max = this.raw.length;
        while(!done && i <= max){
            if(this.raw[i].dataset.rawRef == row.dataset.rawRef){
                this.trash.push(this.raw.splice(i,1)[0]); // Remove elemento do raw e insere no trash
                done = true;
            }
            i++;
        }
        row.remove(); // Remove o elemento da tabela
        if(this.enablePaginate){try {this.tbody.appendChild(this.raw[this.leid]);}catch(error){}} // Adiciona proximo elemento ao final do tbody
        document.getElementById('jsTableRestoreRow').classList.remove('d-none'); // Exibe botao para restaurar linha
    }
    restoreRow(){
        let tr = this.trash.pop();
        tr.classList = 'table-warning';
        if(this.enablePaginate){this.goToPage(this.lastPage)};
        this.tbody.appendChild(tr);
        this.raw.push(tr);
        if(this.trash.length == 0){document.getElementById(`jsTableRestoreRow`).classList.add('d-none');}
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
        let filename = 'jsTable.json';
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
        let filename = 'jsTable.csv';
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
    validateTable(){}
}