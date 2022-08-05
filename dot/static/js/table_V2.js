class jsTable{
    constructor(id, options){
        this.id = typeof id == 'string' ? id : id.id; // Armazena id da tabela
        this.table = typeof id == 'object' ? id : null; // Aponta para tabela alvo
        this.raw = options?.raw || []; // Json com dados para popular tabela
        this.headers = []; // Arrays de strings com o nome dos headers da tabela
        this.thead = this.table ? this.table.tHead : null; // Aponta para thead
        this.tbody = this.table ? this.table.tBodies[0] : null; // Aponta para tbody principal (armazena registros visiveis)
        this.hbody = null; // Aponta para tbody auxiliar que armazena as linhas ocultas pela paginacao
        this.trash = []; // Ao deletar row, registro eh movido para o trash (permitndo retornar registro)
        this.tableClasslist = options?.tableClasslist || 'table border table-striped table-hover caption-top';
        this.editableColsClasslist = options?.editableColsClasslist || 'text-primary';
        this.container = options?.container || document.body; // parentNode da tabela, usado na construcao de tabela pelo evento createTable(), caso nao informado append nova tabela no body
        this.editableCols = options?.editableCols || [];
        this.enablePaginate = options?.enablePaginate != undefined ? options.enablePaginate : false; // Booleno setado para true se paginacao estiver ativa para tabela
        this.rowsPerPage = options?.rowsPerPage || 20; // Quantidade de registros a serem exibidos por pagina
        this.activePage = options?.activePage || 1; // Informa pagina exibida no momento (ou pode ser setada na criacao do objeto)
        this.maxPagesButtons = options?.maxPagesButtons || 6; // Quantidade maxima de botoes a serem exibidos 
        this.paginateControlClasslist = options?.paginateControlsClasslist || 'pagination justify-content-end'; 
        this.paginatePageClasslist = options?.paginatePageClasslist || 'page-item';
        this.paginateLinkClasslist = options?.paginateLinkClasslist || 'page-link';
        this.paginateFirstLabel = options?.paginateFirstLabel || 'Inicio';
        this.paginatePreviousLabel = options?.paginatePreviousLabel || 'Anterior';
        this.paginateNextLabel = options?.paginateNextLabel || 'Proximo';
        this.canAddRow = options?.addRow != undefined ? options.addRow : true;
        this.canDeleteRow = options?.deleteRow != undefined ? options.deleteRow : true;
        this.canExportJson = options?.exportJson != undefined ? options.exportJson : true;
        this.exportBtn = null;
        this.canFilter = options?.canFilter || true;
        this.filterInput = null;
        this.canSort = options?.canSort || true;
        if(this.table == null){
            this.createTable();
            this.buildHeaders();
            this.buildRows();
        }
        else{this.validateTable()}
        // this.buildListeners();
        if(this.enablePaginate){this.paginate()}
    }
    createTable(){
        this.table = document.createElement('table');
        this.table.id = this.id;
        this.table.classList = this.tableClasslist;
        this.table.caption = this.buildControls();
        this.thead = document.createElement('thead');
        this.tbody = document.createElement('tbody');
        this.hbody = document.createElement('tbody');
        this.hbody.classList.add('d-none');
        this.table.appendChild(this.thead);
        this.table.appendChild(this.tbody);
        this.table.appendChild(this.hbody);
        this.container.appendChild(this.table);
    }
    buildHeaders(){
        let tr = document.createElement('tr');
        for(let i = 0;i < this.raw.length;i++){
            for(let j in this.raw[i]){
                if(!this.headers.includes(j)){
                    this.headers.push(j);
                    let th = document.createElement('th');
                    th.setAttribute('data-key',j);
                    th.innerHTML = j[0].toUpperCase() + j.substring(1);
                    tr.appendChild(th);
                }
            }
        }
        if(this.deleteRow){ // Caso habilitado deleteRow, adiciona uma th relativa ao controle
            let th = document.createElement('th');
            th.innerHTML = '';
            tr.appendChild(th);
        }
        this.thead.appendChild(tr);
    }
    buildRows(){
        for(let i = 0;i < this.raw.length;i++){
            let row = document.createElement('tr');
            for(let j = 0;j < this.headers.length;j++){
                let v = this.raw[i][this.headers[j]];
                let col = document.createElement('td');
                col.innerHTML = v != undefined ? v : '';
                col.contentEditable = this.editableCols.includes(this.headers[j]) ? true : false;
                col.classList = this.editableCols.includes(this.headers[j]) ? this.editableColsClasslist : '';
                row.appendChild(col);
            }
            // this.rowAddControls(row);
            this.tbody.appendChild(row);
        }
    }
    appendRows(json){} // Adiciona rows na tabela
    buildControls(){
        if(this.canSort){this.table.classList.add('table-sortable')}
    }
    buildListeners(){}
    setEditableCols(){} // Somente usado em tabelas previamente criadas
    loadData(json){
        this.raw = json;
        this.cleanTable();
        this.buildHeaders();
        this.buildRows();
    }
    filter(){}
    paginate(){
        let pgRows = this.table.querySelectorAll('tbody tr'); // Seleciona os trs de todos os tbodies
        let rowsSize = pgRows.length;
        let pages = Math.ceil(rowsSize / this.rowsPerPage);
        if(this.activePage > pages){this.activePage = pages} // Impede tentativa de acesso de pagina maior que a qtde de paginas
        let feid = (this.activePage - 1) * this.rowsPerPage; // FirstElementId: Seta o ID do primeiro elemento a ser mostrado
        let leid = Math.min((feid + this.rowsPerPage) - 1, pgRows.length - 1); // LastElementId: Seta o ID do ultimo elemento a ser mostrado   
        this.tbody.innerHTML = ''; // Limpa os tbody principal
        this.hbody.innerHTML = ''; // Limpa os tbody auxiliar
        for(let i = 0;i < rowsSize;i++){ // Divide os elementos nos tbody's
            console.log(pgRows[i]);
            // console.log('i: ' + i + ' feid: ' + feid + ' leid: ' + leid);
            if(i >= feid && i <= leid){this.tbody.appendChild(pgRows[i]);}
            else{this.hbody.appendChild(pgRows[i]);}
        }
    }
    pg_buildControls(){}
    addRow(){}
    deleteRow(row){}
    restoreRow(){}
    getRows(){}
    getJson(){}
    exportJson(){}
    getCsv(){}
    cleanTable(){
        this.thead.innerHTML = '';
        this.tbody.innerHTML = '';
    }
    validateTable(){
        if(!this.hbody){ // Caso tabela ainda nao tenha elemento setado para o hbody, cria e insere elemento
            this.hbody = document.createElement('tbody');
            this.hbody.classList.add('d-none');
            this.table.appendChild(this.hbody);           
        }
    }
}