/*
* JsonTable Cria tabela editável de um objeto json
*
* @version  1.0
* @since    17/07/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @example  let usuarios = new JsonTable('usuarios', {option:value});
* @option   json             : json      # Dados em formato json
* @option   container        : element   # Container html onde sera construido a tabela
* @option   editableCols     : array     # Array com nome dos campos (cabecalhos) que seram habilitados para edicao
* @option   tableClasslist   : string    # Classes da tabela (default: 'table border table-striped table-hover caption-top')
* @option   addRow           : bool      # Booleano que define se sera habilitado adicionar novos registros (default: true)
* @option   deleteRow        : bool      # Booleano que define se sera habilitado exclusao de registros (default: true)
* @option   exportJson       : bool      # Booleano que define se sera habilitado download dos dados da tabela (default: true)
*/
class JsonTable{
    constructor(id, options){
        this.id = id;
        this.table = null;
        this.thead = null;
        this.tbody = null;
        this.container = options?.container || document.body; // Caso nao informado container destino cria tabela dentro do body
        this.tableClasslist = options?.tableClasslist || 'table border table-striped table-hover caption-top';
        this.json = options?.json || [];
        this.editableCols = options?.editableCols || [];
        this.headers = [];
        this.addRow = options?.addRow != undefined ? options.addRow : true;
        this.deleteRow = options?.deleteRow != undefined ? options.deleteRow : true;
        this.exportJson = options?.exportJson != undefined ? options.exportJson : true;
        this.exportBtn = null;
        this.trash = [];
        this.createTable();
        this.buildHeaders();
        this.buildRows();
        this.buildListeners();
    }
    createTable(){
        this.table = document.createElement('table');
        this.table.id = this.id;
        this.table.classList = this.tableClasslist;
        this.table.caption = this.buildControls();
        this.thead = document.createElement('thead');
        this.tbody = document.createElement('tbody');
        this.table.appendChild(this.thead);
        this.table.appendChild(this.tbody);
        this.container.appendChild(this.table);
    }
    buildControls(){
        let caption = document.createElement('caption');
        caption.classList = 'text-end';
        caption.innerHTML = '<div class="float-start">Foo</div>';
        if(this.addRow){
            let add = `<span id="tableJsonAddBtn_${this.id}" class="btn btn-sm btn-outline-success" title="Novo registro"><i class="fas fa-plus"></i></span>`;
            caption.innerHTML += add;
        }
        if(this.exportJson){
            let btn = `<span id="tableJsonExportBtn_${this.id}" class="btn btn-sm btn-outline-primary ms-1" title="Baixar arquivo json"><i class="fas fa-download"></i></span>`;
            caption.innerHTML += btn;
        }
        if(this.deleteRow){
            let btn = `<span id="tableJsonRestoreBtn_${this.id}" class="d-none btn btn-sm btn-outline-purple ms-1" title="Retornar ultima exclusão"><i class="fas fa-trash-restore"></i></span>`;
            caption.innerHTML += btn;
        }
        return caption;
    }
    buildListeners(){
        if(this.addRow){document.getElementById(`tableJsonAddBtn_${this.id}`).addEventListener('click', () => this.insertRow());}
        if(this.deleteRow){document.getElementById(`tableJsonRestoreBtn_${this.id}`).addEventListener('click', () => this.restoreLastRow());}
        if(this.exportJson){document.getElementById(`tableJsonExportBtn_${this.id}`).addEventListener('click', () => this.fileExportJson());}
    }
    buildHeaders(){
        let tr = document.createElement('tr');
        for(let i = 0;i < this.json.length;i++){
            for(let j in this.json[i]){
                if(!this.headers.includes(j)){
                    this.headers.push(j);
                    let th = document.createElement('th');
                    th.setAttribute('data-key',j);
                    th.innerHTML = j[0].toUpperCase() + j.substring(1);
                    tr.appendChild(th);
                }
            }
        }
        if(this.deleteRow){
            let th = document.createElement('th');
            th.innerHTML = '';
            tr.appendChild(th);
        }
        this.thead.appendChild(tr);
    }
    buildRows(){
        for(let i = 0;i < this.json.length;i++){
            let row = document.createElement('tr');
            for(let j = 0;j < this.headers.length;j++){
                let v = this.json[i][this.headers[j]];
                let col = document.createElement('td');
                col.innerHTML = v != undefined ? v : '';
                col.contentEditable = this.editableCols.includes(this.headers[j]) ? true : false;
                col.classList = this.editableCols.includes(this.headers[j]) ? 'text-primary' : 'text-muted';
                row.appendChild(col);
            }
            this.rowAddControls(row);
            this.tbody.appendChild(row);
        }
    }
    rowAddControls(row){
        if(this.deleteRow){
            let controls = document.createElement('td');
            controls.classList = 'text-end py-1';
            let deleteBtn = document.createElement('span');
            deleteBtn.classList = 'btn btn-sm btn-outline-secondary';
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.onclick = () => this.moveRowToTrash(row);
            controls.appendChild(deleteBtn);
            row.appendChild(controls);
        }
    }
    insertRow(){
        let tr = document.createElement('tr');
        for(let i = 0;i < this.headers.length;i++){
            let td = document.createElement('td');
            td.innerHTML = '&nbsp;'
            td.contentEditable = true; // No insert row todos os campos sao editaveis
            td.classList = 'text-primary';
            tr.appendChild(td);
        }
        this.rowAddControls(tr);
        this.tbody.appendChild(tr);
    }
    moveRowToTrash(row){
        this.trash.push(row);
        row.remove();
        document.getElementById(`tableJsonRestoreBtn_${this.id}`).classList.remove('d-none');
    }
    restoreLastRow(){
        let tr = this.trash.pop();
        tr.classList.add('table-danger');
        this.tbody.appendChild(tr);
        if(this.trash.length == 0){document.getElementById(`tableJsonRestoreBtn_${this.id}`).classList.add('d-none');}
    }
    getRows(){
        let items = [];
        let trs = this.tbody.querySelectorAll('tr');
        for(let i = 0;i < trs.length;i++){
            let item = {};
            let cols = trs[i].querySelectorAll('td');
            for(let j = 0;j < cols.length - 1;j++){ // cols.length - 1 desconsidera a ultima coluna dos controles
                item[this.headers[j]] = cols[j].innerText.replace('\n', '');
            }
            items[i] = item;
        }
        return items;
    }
    getJson(){return JSON.stringify(this.getRows());}
    fileExportJson(){
        let data = this.getJson();
        let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(data);
        let filename = 'table_json.json';
        let btn = document.createElement('a');
        btn.classList = 'd-none';
        btn.setAttribute('href', dataUri);
        btn.setAttribute('download', filename);
        btn.click();
        btn.remove();
        btn = document.getElementById(`tableJsonExportBtn_${this.id}`);
        let originalClasslist = btn.classList.value;
        let originalHtml = btn.innerHTML;
        btn.classList = 'btn btn-sm btn-success ms-1';
        btn.innerHTML = '<i class="fas fa-check"></i>';
        setTimeout(function() {btn.classList = originalClasslist;btn.innerHTML = originalHtml;}, 2000);
    }
}