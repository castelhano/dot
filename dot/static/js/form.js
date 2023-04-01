/*
* jsForm   Implementa formulario simples para manipular objeto json {key:value}
*
* @version      1.0
* @since        27/01/2023
* @release      27/01/2023 [commit inicial]
* @author       Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @example      {"nome":"Rafael Alves", "Email":"Fooo",...}
* @depend       boostrap 5.2.0, fontawesome 5.15.4, dot.css, dot.js
*/
class jsForm{
    constructor(options){
        // Variaveis internas
        this.legendContainer = null; // Div (col) com conteudo da legenda do form 
        this.controlsContainer = null; // Div container (col) para os botoes
        this.controls = null; // Div (col) para grupo dos botoes do form
        this.formContainer = null; // Div (col) onde eh exibido os campos em exibicao
        this.form = null; // Elemento table
        this.tbody = null; // Elemento tbody
        this.saveBtn = null; // Aponta para o botao salvar
        this.addBtn = null; // Aponta para o botao para adicionar linha
        this.sortBtn = null; // Aponta para o botao de classificar
        this.jsonBtn = null; // Aponta para o botao para exportar json
        // Configuracao
        this.data = options?.data || {key:'value'}; // Json com dados do form
        this.container = options?.container || document.body; // parentNode do form, caso nao informado append no document.body
        this.legend = options?.legend || ''; // String com a legenda do form
        this.readOnly = options?.readOnly != undefined ? options.readOnly : false; // Se definido pata true, desabilita opcao de editar campos, save, sort, etc..
        this.canSave = options?.canSave != undefined ? options.canSave : true; // Se definido para true exibe botao para salvar form
        this.url = options?.url || null; // Url que recebera o json com ajustado no metodo save()
        this.token = options?.token || ''; // Token (caso exista), sera adicionado no header da requisicao, Dica: use getCookie('csrftoken') para buscar o token da pagina 
        this.save = options?.save != undefined ? options.save : () => this.saveJson(); // Funcao definida aqui sera acionada no evento click do botao save
        this.beforeSave = options?.beforeSave != undefined ? options.beforeSave : () => this.beforeSaveJson(); // Funcao definida aqui sera acionada no evento click do botao save
        this.onSuccess = options?.onSuccess != undefined ? options.onSuccess : () => this.onSaveSuccess(); // Funcao a ser acionada em caso de sucesso
        this.onError = options?.onError != undefined ? options.onError : () => this.onSaveError(); // Funcao a ser acionada em caso de erro
        this.canAddRow = options?.canAddRow != undefined ? options.canAddRow : true;
        this.canDeleteRow = options?.canDeleteRow != undefined ? options.canDeleteRow : false; // Se definido para true exibe botao para deletar row
        this.canChangeKey = options?.canChangeKey != undefined ? options.canChangeKey : false;
        this.canSort = options?.canSort != undefined ? options.canSort : true;
        this.canExportJson = options?.canExportJson != undefined ? options.canExportJson : true;
        this.fileName = options?.fileName || 'jsForm.json'; // Nome do arquivo para exportar
        this.canImportFile = options?.canImportFile != undefined ? options.canImportFile : true;
        // Estilizacao
        this.formClassList = options?.formClassList || 'table table-hover border';
        this.formContainerClasslist = 'col';
        this.keyClassList = options?.keyClassList || 'fit pe-5';
        this.valueClassList = options?.valueClassList || 'bg-light border';
        this.textFormEmpty = options?.textFormEmpty || 'Nada a exibir';
        
        this.buildControls(); // Cria controles do form
        this.createForm(); // Cria container para submenus do form e container para campos do form
        this.__refreshData(); // Insere as trs na tabela
        
    }
    createForm(){
        this.form = document.createElement('table');
        this.form.classList = this.formClassList;
        this.tbody = document.createElement('tbody');
        this.form.appendChild(this.tbody);
        this.formContainer = document.createElement('div');
        this.formContainer.classList = this.formContainerClasslist;
        this.formContainer.appendChild(this.form);
        let row = document.createElement('div');
        row.classList = 'row g-2';
        row.appendChild(this.formContainer);
        this.container.appendChild(row);
    }
    buildControls(){
        let row = document.createElement('div'); // Row (flex container)
        row.classList = 'row mb-2';
        this.legendContainer = document.createElement('div'); // Col para legenda (flex item)
        this.legendContainer.classList = 'col';
        this.legendContainer.innerHTML = this.legend;
        this.controlsContainer = document.createElement('div'); // Col para controles (flex item)
        this.controlsContainer.classList = 'col-auto';
        this.controls = document.createElement('div'); // Div para grupo de botoes (btn-group)
        this.controls.classList = 'btn-group';
        if(this.canAddRow && !this.readOnly){
            this.addBtn = document.createElement('button');
            this.addBtn.classList = 'btn btn-sm btn-success px-3';
            this.addBtn.innerHTML = '<i class="fas fa-plus"></i>';
            this.addBtn.onclick = () => this.addRow();
            this.controls.appendChild(this.addBtn);
        }
        if(this.canSave && !this.readOnly){
            this.saveBtn = document.createElement('button');
            this.saveBtn.classList = 'btn btn-sm btn-primary px-3';
            this.saveBtn.innerHTML = '<i class="fas fa-save"></i>';
            this.saveBtn.onclick = () => this.save();
            this.controls.appendChild(this.saveBtn);
        }
        if(this.canSort && !this.readOnly){
            this.sortBtn = document.createElement('button');
            this.sortBtn.classList = 'btn btn-sm btn-warning px-3';
            this.sortBtn.innerHTML = '<i class="fas fa-sort-amount-down"></i>';
            this.sortBtn.onclick = () => this.sort();
            this.controls.appendChild(this.sortBtn);
        }
        if(this.canImportFile){
            this.importBtn = document.createElement('button');
            this.importBtn.classList = 'btn btn-sm btn-danger px-3';
            this.importBtn.innerHTML = '<i class="fas fa-upload"></i>';
            this.importBtn.onclick = (e) => {
                let inputFile = document.createElement('input');
                inputFile.type = 'file';
                inputFile.style.display = 'none';
                inputFile.accept = '.json';
                let obj = this;
                inputFile.onchange = () => {
                    let fr = new FileReader();
                    fr.onload = (function(){
                        obj.loadData(JSON.parse(fr.result));
                        inputFile.remove();
                        obj.__refreshData();
                    });
                    fr.readAsText(inputFile.files[0]);
                };
                inputFile.click();
            };
            this.controls.appendChild(this.importBtn);
        }
        if(this.canExportJson){
            this.jsonBtn = document.createElement('button');
            this.jsonBtn.classList = 'btn btn-sm btn-secondary';
            this.jsonBtn.innerHTML = '<i class="fas fa-download me-2"></i> JSON';
            this.jsonBtn.onclick = (e) => this.exportJson(e);
            this.controls.appendChild(this.jsonBtn);
        }
        this.controlsContainer.appendChild(this.controls);
        row.appendChild(this.legendContainer);
        row.appendChild(this.controlsContainer);
        this.container.appendChild(row);
    }
    __refreshData(){
        for(let item in this.data){
            let tr = document.createElement('tr');
            let th = document.createElement('th');
            th.classList = this.keyClassList;
            th.innerHTML = item;
            if(this.canChangeKey){th.contentEditable = true}
            let td = document.createElement('td');
            td.classList = this.valueClassList;
            if(!this.readOnly)(td.contentEditable = true);
            td.innerHTML = this.data[item];
            tr.appendChild(th);
            tr.appendChild(td);
            if(this.canDeleteRow){ // Adiciona botar para deletar caso habilitado funcao
                let td_controls = document.createElement('td');
                td_controls.classList = 'text-end fit pb-0 py-1';
                let btnDeleteRow = document.createElement('button');
                btnDeleteRow.classList = 'btn btn-sm btn-danger';
                btnDeleteRow.innerHTML = '<i class="fas fa-trash"></i>';
                btnDeleteRow.onclick = () => this.__deleteRow(tr);
                btnDeleteRow.tabIndex = '-1';
                td_controls.appendChild(btnDeleteRow);
                tr.appendChild(td_controls);
            }
            this.tbody.appendChild(tr);
        }
    }
    loadData(data){
        this.cleanForm();
        this.data = data;
    }
    addRow(){
        this.tbody.querySelectorAll('[data-type=emptyRow]').forEach((e) => {e.remove();}) // Remove emptyRow (caso exista)
        let tr = document.createElement('tr');
        let th = document.createElement('th');
        th.classList = this.keyClassList;
        th.contentEditable = true;
        th.innerHTML = '';
        let td = document.createElement('td');
        td.classList = this.valueClassList;
        td.contentEditable = true;
        td.innerHTML = '';
        tr.appendChild(th);
        tr.appendChild(td);
        if(this.canDeleteRow){ // Adiciona botar para deletar caso habilitado funcao
            let td_controls = document.createElement('td');
            td_controls.classList = 'text-end fit pb-0 py-1';
            let btnDeleteRow = document.createElement('button');
            btnDeleteRow.classList = 'btn btn-sm btn-danger';
            btnDeleteRow.innerHTML = '<i class="fas fa-trash"></i>';
            btnDeleteRow.onclick = () => this.__deleteRow(tr);
            btnDeleteRow.tabIndex = '-1';
            td_controls.appendChild(btnDeleteRow);
            tr.appendChild(td_controls);
        }
        this.tbody.appendChild(tr);
        th.focus();
    }
    sort(asc=true){
        let rows = Array.from(this.tbody.querySelectorAll('tr')); // Carrega todas as linhas do grupo em foco
        if(!rows){ return null } // Se tabela for vazia, termina processo
        const modifier = asc ? 1 : -1; // Modificador para classificar em order crecente (asc=true) ou decrescente (asc=false)
        const sortedRows = rows.sort((a, b) => {
            const aColText = a.querySelector(`th:nth-child(1)`).textContent.trim().toLowerCase();
            const bColText = b.querySelector(`th:nth-child(1)`).textContent.trim().toLowerCase();
            return aColText > bColText ? (1 * modifier) : (-1 * modifier);
        });
        rows = sortedRows; // Atualiza campos
        rows.forEach((e) => this.tbody.append(e)); // Atualiza o tbody   
    }
    saveJson(){
        if(this.url){
            if(!this.__validateForm()){return false;}
            if(!this.beforeSave()){return false;} // Chama metodo beforeSave antes de executar codigo, espera retorno true para dar sequencia
            let btnSave = this.saveBtn; // Workaround para acessar botao save dentro da funcao ajax
            let onSuccess = this.onSuccess; // Workaround para acessar funcao dentro da funcao ajax
            let onError = this.onError; // Workaround para acessar funcao dentro da funcao ajax
            let xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function() {
                if(this.readyState == 4 && this.status == 200){onSuccess();}
                else if(this.readyState == 4){onError(this.status);}
            };
            xhttp.open("POST", `${this.url}`, true);
            xhttp.setRequestHeader('X-CSRFToken', this.token);
            xhttp.send(JSON.stringify(this.getJson()));
        }
        else{console.log("jsForm: Informe nas opcoes a url (POST) que ira receber o json {url: 'minha/url'} ou defina uma funcao personalizada {save: suaFuncao}");}
    }
    beforeSaveJson(){return true}
    onSaveSuccess(){try {dotAlert('success', 'Arquivo salvo com <b>sucesso</b>');}catch(e){}} // Caso finalizado com sucesso, tenta chamar metodo de alerta
    onSaveError(status){try {dotAlert('danger', `<b>Erro</b> ao salvar o arquivo. [ <b>${status}</b> ]`);}catch(e){}} // Caso finalizado com erro, tenta chamar metodo de alerta
    __deleteRow(tr){
        tr.remove();
        if(this.tbody.innerHTML == ''){this.tbody.innerHTML = `<tr data-type="emptyRow"><td colspan="2" class="${this.valueClassList}">${this.textFormEmpty}</td></tr>`;}
    }
    getJson(){
        this.__updateData();
        return this.data;
    }
    __updateData(){ // Atualiza this.data
        let newData = {}; // Inicia novo array (json)
        this.tbody.querySelectorAll('tr').forEach((e) => { // Atualiza dados em newData
            if(!e.dataset.type ||  e.dataset.type != 'emptyRow'){newData[e.firstChild.innerHTML] = e.children[1].innerHTML;}
            this.data = newData;
        });
    }
    exportJson(e){
        if(!this.__validateForm()){return false;}
        this.__updateData();
        let data = JSON.stringify(this.getJson());
        let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(data);
        let filename = this.fileName;
        let btn = document.createElement('a');
        btn.style.display = 'none';
        btn.setAttribute('href', dataUri);
        btn.setAttribute('download', filename);
        btn.click();
        btn.remove();
        if(this.canExportJson){
            let originalClasslist = e.target.className;
            e.target.classList = 'btn btn-sm btn-success';
            setTimeout(function() {e.target.classList = originalClasslist;}, 800);
        }
        try {dotAlert('success', 'Arquivo <b>json</b> gerado com <b>sucesso</b>')}catch(error){}
    }
    __validateForm(){
        let has_errors = false;
        let key_names = []; // Armazena chaves (name) do objeto json
        this.tbody.querySelectorAll('tr').forEach((e) => {
            if(e.firstChild.innerHTML.trim() == '' || key_names.includes(e.firstChild.innerHTML)){
                e.firstChild.classList.add('table-danger');
                has_errors = true;
            }
            else{key_names.push(e.firstChild.innerHTML)}
        });
        if(has_errors){
            dotAlert('danger', '<b>Erro:</b> Chave duplicada ou vazia, corrija antes de prosseguir');
        }
        return !has_errors;
    }
    cleanForm(){
        this.tbody.innerHTML = '';
    }
    
}