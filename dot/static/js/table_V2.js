class jsTable{
    constructor(id, options){
        this.id = typeof id == 'string' ? id : id.id; // Armazena id da tabela
        this.table = typeof id == 'object' ? id : null; // Aponta para tabela alvo
        this.headers = [];
        this.tbody = this.table.tBodies[0] || null; // Aponta para tbody principal (armazena registros visiveis)
        this.hbody = this.table.tBodies[1] || null; // Aponta para tbody auxiliar (armazena registros ocultos pela funcao paginate)
        this.trash = []; // Ao deletar row, registro eh movido para o trash (permitndo retornar registro)
        this.raw = options?.raw || []; // JSON COM DADOS PARA POPULAR TABELA
        this.tableClasslist = options?.tableClasslist || 'table border table-striped table-hover caption-top';
        this.container = options?.container || document.body; // parentNode da tabela, usado na construcao de tabela pelo evento createTable(), caso nao informado append nova tabela no body
        this.editableCols = options?.editableCols || [];
        this.paginateOn = false; // Booleno setado para true se paginacao estiver ativa para tabela
        this.rowsPerPage = options?.rowsPerPage || 20; // Quantidade de registros a serem exibidos por pagina
        this.activePage = options?.activePage || 1; // Informa pagina exibida no momento (ou pode ser setada na criacao do objeto)
        this.maxPagesButtons = options?.maxPagesButtons || 6; // Quantidade maxima de botoes a serem exibidos 
        this.paginateControlClasslist = options?.paginateControlsClasslist || 'pagination justify-content-end'; 
        this.paginatePageClasslist = options?.paginatePageClasslist || 'page-item';
        this.paginateLinkClasslist = options?.paginateLinkClasslist || 'page-link';
        this.paginatePreviousLabel = options?.paginatePreviousLabel || 'Anterior';
        this.paginateNextLabel = options?.paginateNextLabel || 'Proximo';
        this.pages = null; // Variavel usada pelo metodo paginate(), armazena a quantidade todal de paginas da tabela
        this.canAddRow = options?.addRow != undefined ? options.addRow : true;
        this.canDeleteRow = options?.deleteRow != undefined ? options.deleteRow : true;
        this.canExportJson = options?.exportJson != undefined ? options.exportJson : true;
        this.exportBtn = null;
        this.canFilter = options?.canFilter || true;
        this.filterInput = null;
        // this.createTable();
        // this.buildHeaders();
        // this.buildRows();
        // this.buildListeners();
    }
    createTable(){}
    buildHeaders(){}
    buildRows(){}
    buildControls(){}
    buildListeners(){}
    setEditableCols(){} // Somente usado em tabelas previamente criadas
    loadData(){} // Carrega dados json na tabela (para carregar registros apos criacao da tabela)
    filter(){}
    addRow(){}
    deleteRow(row){}
    restoreRow(){}
    getRows(){}
    getJson(){}
    exportJson(){}
    getCsv(){}
}