/*
* jsFormx   Implementa formulario para manipular objeto json (extrutura predefinida)
*
* @version      2.0
* @since        02/09/2022
* @release      27/01/2023 [alterado layout do json integrado schema em this.data, modificado metodos]
* @author       Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @example      [{"name":"nome","value":"Rafael Alves",schema:{}},{"name":"email","schema"{"group":"Contato","email":"c@gmail.com"}}, .....]
* @depend       boostrap 5.2.0, fontawesome 5.15.4, dot.css, dot.js
*/
class jsFormx{
    constructor(options){
        // Variaveis internas
        this.legendContainer = null; // Div (col) com conteudo da legenda do form 
        this.controlsContainer = null; // Div container (col) para os botoes
        this.controls = null; // Div (col) para grupo dos botoes do form
        this.groupsMenu = null; // Menu dos grupos do form
        this.formContainer = null; // Div (col) onde eh exibido os campos em exibicao
        this.form = null; // Elemento table
        this.tbody = null; // Elemento tbody
        this.groups = []; // Array com nome dos grupos
        this.groupOnFocus = null; // String que armazena o nome do grupo em exibicao no momento
        this.saveBtn = null; // Aponta para o botao salvar
        this.addBtn = null; // Aponta para o botao para adicionar linha
        this.schemaBtn = null; // Aponta para o botao de exibir o schema
        this.sortBtn = null; // Aponta para o botao de classificar
        this.jsonBtn = null; // Aponta para o botao para exportar json
        this.editingSchema = false; // Indica se esta sendo editado schema neste momento (usado para travar algumas operacoes)
        // Configuracao
        this.data = options?.data || [{name:'Key', value:"Value",schema:{}}]; // Json com dados do form
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
        this.enableDuplicates = options?.enableDuplicates != undefined ? options.enableDuplicates : false;
        this.canChangeSchema = options?.canChangeSchema != undefined ? options.canChangeSchema : true;
        this.canSort = options?.canSort != undefined ? options.canSort : true;
        this.canExportJson = options?.canExportJson != undefined ? options.canExportJson : true;
        this.canImportFile = options?.canImportFile != undefined ? options.canImportFile : true;
        // Estilizacao
        this.formClassList = options?.formClassList || 'table table-hover border';
        this.groupsMenuClasslist = 'col-auto';
        this.formContainerClasslist = 'col';
        this.keyClassList = options?.keyClassList || 'fit pe-5';
        this.valueClassList = options?.valueClassList || 'bg-light border';
        this.textFormEmpty = options?.textFormEmpty || 'Nada a exibir';
        
        this.buildControls(); // Cria controles do form
        this.createForm(); // Cria container para submenus do form e container para campos do form
        this.buildGroupMenu(); // Monta o menu dos grupos
        this.buildListeners(); // Adiciona os listeners para evento click dos menus
        this.showGroup(this.groupOnFocus, false); // Exibe o primeiro grupo disponivel
        
    }
    createForm(){
        this.form = document.createElement('table');
        this.form.classList = this.formClassList;
        this.tbody = document.createElement('tbody');
        this.form.appendChild(this.tbody);
        this.groupsMenu = document.createElement('div');
        this.groupsMenu.classList = this.groupsMenuClasslist;
        this.formContainer = document.createElement('div');
        this.formContainer.classList = this.formContainerClasslist;
        this.formContainer.appendChild(this.form);
        let row = document.createElement('div');
        row.classList = 'row g-2';
        row.appendChild(this.groupsMenu);
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
        if(this.canChangeSchema && !this.readOnly){
            this.schemaBtn = document.createElement('button');
            this.schemaBtn.classList = 'btn btn-sm btn-purple';
            this.schemaBtn.innerHTML = '<i class="fas fa-tags me-2"></i> Schema';
            this.schemaBtn.onclick = () => this.loadSchema();
            this.controls.appendChild(this.schemaBtn);
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
    buildGroupMenu(){
        let list_itens = '';
        for(let item in this.data){ // Percorre todos os itens para popular os grupos
            if(this.data[item].schema?.group){this.groups.push(this.data[item].schema.group);} // Se item tem grupo definido, carrega grupo no array
            else{this.data[item].schema.group = 'Geral';this.groups.push('Geral');} // Caso nao, atualiza campo para grupo geral e adiciona geral ao array
        }
        this.groups = [...new Set(this.groups)]; // Remove duplicatas no array

        if(this.groups.includes('Geral')){
            let geral = this.groups.splice(this.groups.indexOf('Geral'), 1); // Remove o grupo geral da lista (sera inserido logo no inicio)
            this.groups.sort(); // Reordena o array em ordem alfabetica
            this.groups.splice(0, 0 , 'Geral'); // Reincere o geral no inicio do array
        }
        for(let i = 0; i < this.groups.length;i++){ // Insere os links para os grupos
            list_itens += `<a data-type="group-link" data-groupname="${this.groups[i]}" class="list-group-item list-group-item-action pointer">${this.groups[i]}</a>`;
        }
        let list = `<div class="col-auto" style="min-width: 180px;"><div class="list-group" id="list-tab" role="tablist">${list_itens}</div></div>`;
        this.groupsMenu.innerHTML = list;
        this.groupOnFocus = this.groups[0]; // Move o foco para o primeiro grupo cadastrado
    }
    buildListeners(){
        let links = this.groupsMenu.querySelectorAll('[data-type="group-link"]');
        for(let i = 0;i < links.length;i++){
            links[i].addEventListener('click', () => this.showGroup(`${links[i].dataset.groupname}`));
        }
    }
    loadData(data){
        this.cleanForm();
        this.data = data;
        this.buildGroupMenu();
        this.buildListeners();
        this.showGroup(this.groups[0], false);
    }
    showGroup(group, update=true){ // Carrega campos do respectivo grupo no form
        if(this.editingSchema){return false} // Trava operacao se estiver na edicao do schema
        if(update){this.__updateData();} // Salva alteracoes antes de exibir proximo grupo
        if(!this.groups.includes(group)){dotAlert('danger', '<b>Erro</b> Grupo informado inexistente', false);return false;} // Verifica se grupo existe, caso não exibe msg de erro
        this.tbody.innerHTML = '';
        this.groupOnFocus = group;
        for(let item in this.data){
            if(this.data[item].schema?.group == group){ // Se item for do grupo em foco exibe linha no form
                let tr = document.createElement('tr');
                tr.dataset.schema = JSON.stringify(this.data[item].schema);
                let th = document.createElement('th');
                th.setAttribute('data-originalName', this.data[item].name);
                th.classList = this.keyClassList;
                th.innerHTML = this.data[item].name;
                if(this.canChangeKey){th.contentEditable = true}
                let td = document.createElement('td');
                td.classList = this.valueClassList;
                if(!this.readOnly)(td.contentEditable = true);
                td.innerHTML = this.data[item].value;
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
        if(this.tbody.innerHTML == ''){this.tbody.innerHTML = `<tr data-type="emptyRow"><td colspan="2" class="${this.valueClassList}">${this.textFormEmpty}</td></tr>`;}
        try {this.container.querySelector(`[data-type=group-link].active`).classList.remove('active');}catch (e){} // Se existir grupo ativo, revome classe active
        this.container.querySelector(`[data-groupname=${group}]`).classList.add('active'); // Adiciona classe active ao grupo alvo
    }
    previousGroup(){
        if(this.editingSchema){return false} // Trava operacao se estiver na edicao do schema
        let index = this.groups.indexOf(this.groupOnFocus);
        if(index > 0){this.showGroup(this.groups[index-1])}
    }
    nextGroup(){
        if(this.editingSchema){return false} // Trava operacao se estiver na edicao do schema
        let index = this.groups.indexOf(this.groupOnFocus);
        if(index + 1 < this.groups.length){this.showGroup(this.groups[index+1])}
    }
    addRow(){
        this.tbody.querySelectorAll('[data-type=emptyRow]').forEach((e) => {e.remove();})
        let tr = document.createElement('tr');
        tr.dataset.schema = '{"group":"Geral"}';
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
        else{console.log("jsFormx: Informe nas opcoes a url (POST) que ira receber o json {url: 'minha/url'} ou defina uma funcao personalizada {save: suaFuncao}");}
    }
    beforeSaveJson(){return true}
    onSaveSuccess(){try {dotAlert('success', 'Arquivo salvo com <b>sucesso</b>');}catch(e){}} // Caso finalizado com sucesso, tenta chamar metodo de alerta
    onSaveError(status){try {dotAlert('danger', `<b>Erro</b> ao salvar o arquivo. [ <b>${status}</b> ]`);}catch(e){}} // Caso finalizado com erro, tenta chamar metodo de alerta
    loadSchema(){
        this.editingSchema = true;
        this.__updateData(); // Atualiza this.data
        this.tbody.innerHTML = '';
        this.groupsMenu.classList.add('d-none'); // Oculta os botoes do form
        this.controls.classList.add('d-none'); // Oculta o menu dos grupos
        let btnSaveSchema = document.createElement('button');
        btnSaveSchema.classList = 'btn btn-sm btn-success me-1';
        btnSaveSchema.innerHTML = '<i class="fas fa-save me-2"></i> Salvar';
        btnSaveSchema.setAttribute('data-type', 'btnSaveSchema');
        btnSaveSchema.onclick = () => this.__saveSchema();
        let cancel = document.createElement('button');
        cancel.classList = 'btn btn-sm btn-secondary';
        cancel.innerHTML = 'Cancelar';
        cancel.setAttribute('data-type', 'cancelSchemaBtn');
        cancel.onclick = () => this.__endSchemaEdit();
        this.controlsContainer.appendChild(btnSaveSchema);
        this.controlsContainer.appendChild(cancel);
        for(let i in this.data){
            let tr = document.createElement('tr');
            let th = document.createElement('th');
            th.classList = this.keyClassList;
            th.innerHTML = this.data[i].name;
            let td = document.createElement('td');
            td.classList = this.valueClassList;
            let attrs = this.data[i].schema;
            for(let item in attrs){
                let label_text = `<span class="jsFormExtra-label-name bg-dark text-white user-select-none">${item}</span><span style="display: none;">=</span><span class="jsFormExtra-label-status bg-warning cursor-text" contenteditable="true">${attrs[item]}</span>`;
                let label = document.createElement('label');
                label.classList = 'jsFormExtra-label opacity-75';
                label.innerHTML = label_text;
                label.ondblclick = (e) => {if(e.ctrlKey){e.preventDefault();label.remove();}};
                td.appendChild(label);
            }
            let addBtn = document.createElement('span');
            addBtn.classList = 'bg-light border rounded-circle px-2 py-1 pointer';
            addBtn.innerHTML = '<i class="fas fa-plus text-muted"></i>';
            addBtn.onclick = (e) => this.__addKeyOnSchema(e.target);
            td.appendChild(addBtn);
            let helper_text = document.createElement('span');
            helper_text.classList = 'ms-1 text-muted fs-8';
            helper_text.innerHTML = 'Crtl + Double click para remover';
            td.appendChild(helper_text);
            tr.appendChild(th);
            tr.appendChild(td);
            this.tbody.appendChild(tr);
        }
    }
    __addKeyOnSchema(target){
        if(target.tagName != 'SPAN'){target = target.parentElement} // Trata caso evento pegue o elemento I ao inves do SPAN
        let label = document.createElement('div');
        label.classList = 'jsFormExtra-label' ;
        label.innerHTML = '<span class="jsFormExtra-label-name bg-success text-white" contenteditable="true">key</span><span style="display: none;">=</span><span class="jsFormExtra-label-status bg-warning" contenteditable="true">value</span>';
        label.ondblclick = (e) => {if(e.ctrlKey){e.preventDefault();label.remove();}};
        target.before(label);
    }
    __saveSchema(){
        if(!this.editingSchema){return false;}
        let trs = this.tbody.querySelectorAll('tr');
        let size = trs.length;
        let newGroups = false;
        for(let i = 0; i < size; i++){ // Salva no dicionario schema dados ajustados
            let schema = {};
            trs[i].querySelectorAll('.jsFormExtra-label').forEach((e)=>{
                schema[e.textContent.split('=')[0]] = e.textContent.split('=')[1];
            });
            let key = trs[i].querySelector('th').innerText;
            this.data[i].schema = schema;
            if(!this.groups.includes(schema.group)){newGroups = true;}
        }
        if(newGroups){this.buildGroupMenu();this.buildListeners();} // Se inserido novo grupo, refaz menu
        this.__endSchemaEdit(); // Fecha schema e reexibe form
    }
    __endSchemaEdit(){
        this.tbody.innerHTML = '';
        document.querySelectorAll('[data-type=btnSaveSchema],[data-type=cancelSchemaBtn]').forEach((e) => e.remove()); // Remove os botoes para gravar e cancelar schema
        this.groupsMenu.classList.remove('d-none'); // Reexibe os botoes do form
        this.controls.classList.remove('d-none'); // Reexibe o menu dos grupos
        this.editingSchema = false;
        this.showGroup(this.groupOnFocus, false);
    }
    __deleteRow(tr){
        tr.remove();
        if(this.tbody.innerHTML == ''){this.tbody.innerHTML = `<tr data-type="emptyRow"><td colspan="2" class="${this.valueClassList}">${this.textFormEmpty}</td></tr>`;}
    }
    getJson(){
        if(this.editingSchema){console.log('jsFormx: Comando desativado enquanto edita schema'); return false;} // Ignora comando enquanto editando esquema 
        this.__updateData();
        return this.data;
    }
    __updateData(){ // Atualiza this.data
        let newData = []; // Inicia novo array (json)
        for(let item in this.data){if(this.data[item].schema.group != this.groupOnFocus){newData.push(this.data[item]);}} // Para itens que nao estao em foco apenas copia para novo array
        this.tbody.querySelectorAll('tr').forEach((e) => { // Para os itens em foco (tbody) atualiza dados antes de inserir no array
            if(!e.dataset.type ||  e.dataset.type != 'emptyRow'){newData.push({'name':e.firstChild.innerHTML,'value':e.children[1].innerHTML,'schema':JSON.parse(e.dataset.schema)});}
        });
        this.data = newData;
    }
    exportJson(e){
        this.__updateData();
        if(!this.__validateForm()){return false;}
        let data = JSON.stringify(this.getJson());
        let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(data);
        let filename = 'form_extra.json';
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
        for(let item in this.data){
            if(this.data[item].name.trim() == '' || !this.enableDuplicates && key_names.includes(this.data[item].name)){
                this.data[item].has_error = true;
                has_errors = true;
            }
            else{key_names.push(this.data[item].name)}
        }
        if(has_errors){
            dotAlert('danger', '<b>Erro:</b> Chave duplicada ou vazia, corrija antes de prosseguir');
            this.showGroup(this.groupOnFocus, false);
        }
        return !has_errors;
    }
    cleanForm(){
        this.tbody.innerHTML = '';
        this.groups = [];
    }
    
}