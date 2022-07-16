class JsonTable{
    constructor(id, options){
        this.id = id;
        this.table = null;
        this.thead = null;
        this.tbody = null;
        this.container = options?.container || document.body; // Caso nao informado container destino cria tabela dentro do body
        this.tableClasslist = options?.tableClasslist || 'table border table-striped table-hover caption-top table-sortable';
        this.json = options?.json || [];
        this.editableCols = options?.editableCols || [];
        this.headers = [];
        this.addRow = options?.addRow != undefined ? options.addRow : true;
        this.deleteRow = options?.deleteRow != undefined ? options.deleteRow : true;
        this.trash = [];
        this.createTable();
        this.buildHeaders();
        this.buildRows();
        this.getRows = function(){return tableJsonGetRows(this.headers, this.tbody);} // Retorna array com dados da tabela
        this.getJson = function(){return JSON.stringify(tableJsonGetRows(this.headers, this.tbody));} // Retorna json com dados da tabela
        this.addRow = function(){console.log('FIIIII');};
    }
    // addRow(){
    //     let tr = document.createElement('tr');
    //     for(let i = 0;i < this.headers.length;i++){
    //         let td = document.createElement('td');
    //         td.contentEditable = this.editableCols.includes(this.headers[i]) ? true : false;
    //         td.classList = this.editableCols.includes(this.headers[i]) ? 'text-primary' : 'text-muted';
    //         tr.appendChild(td);
    //     }
    //     this.tbody.appendChild(tr);
    // }
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
        if(this.addRow){
            let onclick = this.addRow;
            let add = `<span class="btn btn-sm btn-outline-success" ${onclick}><i class="fas fa-plus"></i></span>`
            caption.innerHTML += add;
        }
        return caption;
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
            if(this.deleteRow){
                let controls = document.createElement('td');
                controls.classList = 'text-end py-1';
                let deleteBtn = document.createElement('span');
                deleteBtn.classList = 'btn btn-sm btn-outline-secondary';
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.onclick = function(){tableJsonDeleteRow(row)};
                controls.appendChild(deleteBtn);
                row.appendChild(controls);
            }
            this.tbody.appendChild(row);
        }
    }
}
function tableJsonDeleteRow(row){row.remove();}
function tableJsonGetRows(headers,tbody){
    let items = [];
    let trs = tbody.querySelectorAll('tr');
    for(let i = 0;i < trs.length;i++){
        let item = {};
        let cols = trs[i].querySelectorAll('td');
        for(let j = 0;j < cols.length - 1;j++){ // cols.length - 1 desconsidera a ultima coluna dos controles
            item[headers[j]] = cols[j].innerText.replace('\n', '');
        }
        items[i] = item;
    }
    return items;
}