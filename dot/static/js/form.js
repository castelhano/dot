/*
* jsForm   Implementa formulario para manipular objeto json (extrutura predefinida)
*
* @version      1.0
* @since        02/09/2022
* @author       Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @description  Exige json com campos "name" e "value" (demais campos opcionais)
* @example      [{"name":"nome","value":"Rafael Alves"},{"name":"email","value":"c@gmail.com", "group":"Contato"}, .....]
* @depend       boostrap 5.2.0, fontawesome 5.15.4, dot.css, dot.js
*/
class jsForm{
    constructor(options){
        // Variaveis internas
        this.legendContainer = null; // Div (col) com conteudo da legenda do form 
        this.controlsContainer = null; // Div container (col) para os botoes
        this.controls = null; // Div (col) para grupo dos botoes do form
        this.groupsMenu = null; // Menu dos grupos do form
        this.formContainer = null; // Div (col) onde eh exibido os campos em exibicao
        this.form = null; // Elemento table
        this.tbody = null; // Elemento tbody
        this.groups = {}; // Dicionario com os grupos (e seus respectivos campos) {nomeGrupo:[tr,tr,tr...]}
        this.schema = {}; // Dicionario com os schemas {fieldName: "type=text;name=foo;value=55"}
        this.groupOnFocus = null; // String que armazena o nome do grupo em exibicao no momento
        this.saveBtn = null; // Aponta para o botao salvar
        this.addBtn = null; // Aponta para o botao para adicionar linha
        this.schemaBtn = null; // Aponta para o botao de exibir o schema
        this.sortBtn = null; // Aponta para o botao de classificar
        this.jsonBtn = null; // Aponta para o botao para exportar json
        this.editingSchema = false; // Indica se esta sendo editado schema neste momento (usado para travar algumas operacoes)
        // Configuracao
        this.data = options?.data || []; // Json com dados do form
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
        // Estilizacao
        this.formClassList = options?.formClassList || 'table table-hover border';
        this.groupsMenuClasslist = 'col-auto';
        this.formContainerClasslist = 'col';
        this.keyClassList = options?.keyClassList || 'fit pe-5';
        this.valueClassList = options?.valueClassList || 'bg-light border';
        this.textFormEmpty = options?.textFormEmpty || 'Nada a exibir';
        
        this.buildControls(); // Cria controles do form
        this.createForm(); // Cria container para submenus do form e container para campos do form
        this.buildRows(); // Cria fields do form no respectivo grupo 
        this.buildGroupMenu(); // Monta o menu dos grupos
        this.buildListeners(); // Adiciona os listeners para evento click dos menus
        
        // Exibe um grupo
        let [group] = 'Geral' in this.groups ? ['Geral'] : Object.keys(this.groups); // Seleciona o grupo Geral (caso exista) ou o primeiro grupo cadastrado
        if(group && group.length > 0){this.groupFocus(group);} // Exibe grupo
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
        let grupos = Object.keys(this.groups);
        let list_itens = '';
        if(grupos.includes('Geral')){
            grupos = grupos.filter((e) => {return e != 'Geral'}); // Remove o grupo geral da lista (sera inserido logo no inicio)
            list_itens = '<a data-type="group-link" data-groupname="Geral" class="list-group-item list-group-item-action pointer">Geral</a>';
        }
        for(let i = 0; i < grupos.length;i++){
            list_itens += `<a data-type="group-link" data-groupname="${grupos[i]}" class="list-group-item list-group-item-action pointer">${grupos[i]}</a>`;
        }
        let list = `<div class="col-auto" style="min-width: 180px;"><div class="list-group" id="list-tab" role="tablist">${list_itens}</div></div>`;
        this.groupsMenu.innerHTML = list;
    }
    buildRows(){
        this.cleanForm();
        if(this.data.length == 0){
            this.tbody.innerHTML = `<tr><td colspan="2" class="${this.valueClassList}">${this.textFormEmpty}</td></tr>`
            return false;
        }
        for(let item in this.data){ // Percorre todas as linhas alocando cada registro no respectivo grupo
            let tr = document.createElement('tr');
            let th = document.createElement('th');
            th.setAttribute('data-originalName', this.data[item].name);
            th.classList = this.keyClassList;
            th.innerHTML = this.data[item].name;
            if(this.canChangeKey){th.contentEditable = true}
            let td = document.createElement('td');
            let schema = '';
            let avoid = ['name', 'value']; // Para name e value sera considerado conteudo alterado (se alterado) pelo usuario
            for(let attr in this.data[item]){if(!avoid.includes(attr)){schema += `${attr}=${this.data[item][attr]};`}}
            this.schema[this.data[item].name.replace(' ', '_')] = schema.slice(0, -1); // Adiciona string com schema (slice remove ; no final do texto)
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
                td_controls.appendChild(btnDeleteRow);
                tr.appendChild(td_controls);
            }
            if(this.data[item].group == undefined){ // Se nao existe grupo associado adicona linha no grupo Geral
                if('Geral' in this.groups){this.groups.Geral.push(tr);}
                else{this.groups['Geral'] = [tr];} // Caso ainda nao exista registro para o grupo, insere no dicionario
            }
            else{ // Caso exista grupo, insere a linha no respectivo grupo -> this.groups
                if(this.data[item].group in this.groups){this.groups[this.data[item].group].push(tr)} // Se grupo ja tem registros faz append na tr para o grupo
                else{this.groups[this.data[item].group] = [tr];} // Caso ainda nao exista registro para o grupo, insere no dicionario
            }
        }
    }
    buildListeners(){
        let links = this.groupsMenu.querySelectorAll('[data-type="group-link"]');
        for(let i = 0;i < links.length;i++){
            links[i].addEventListener('click', () => this.groupFocus(`${links[i].dataset.groupname}`));
        }
    }
    loadData(data){
        this.data = data;
        this.buildRows();
        this.buildGroupMenu();
        this.buildListeners();
        let [group] = 'Geral' in this.groups ? ['Geral'] : Object.keys(this.groups); // Seleciona o grupo Geral (caso exista) ou o primeiro grupo cadastrado
        if(group && group.length > 0){this.groupFocus(group);} // Exibe grupo
    }
    groupFocus(group){ // Carrega campos do respectivo grupo no form
        if(this.editingSchema){return false} // Trava operacao se estiver na edicao do schema
        this.tbody.innerHTML = '';
        this.groupOnFocus = group;
        try{this.groupsMenu.querySelector('[data-type="group-link"].active').classList.remove('active');}catch(e){} // Caso acionado na criacao da tabela vai gerar excecao pois nao existe nenhum ativo
        this.groupsMenu.querySelector(`[data-groupname="${group}"]`).classList.add('active');
        this.groups[group].forEach(e => { this.tbody.appendChild(e)});
    }
    previousGroup(){
        if(this.editingSchema){return false} // Trava operacao se estiver na edicao do schema
        let grupos = Object.keys(this.groups);
        let index = grupos.indexOf(this.groupOnFocus);
        if(index > 0){this.groupFocus(grupos[index-1])}
    }
    nextGroup(){
        if(this.editingSchema){return false} // Trava operacao se estiver na edicao do schema
        let grupos = Object.keys(this.groups);
        let index = grupos.indexOf(this.groupOnFocus);
        if(index + 1 < grupos.length){this.groupFocus(grupos[index+1])}
    }
    addRow(){
        let tr = document.createElement('tr');
        let th = document.createElement('th');
        th.classList = this.keyClassList;
        th.contentEditable = true;
        th.innerHTML = '';
        let td = document.createElement('td');
        td.classList = this.valueClassList;
        td.contentEditable = true;
        td.setAttribute('type', 'text');
        td.dataset.type = 'newRow';
        td.innerHTML = '';
        tr.appendChild(th);
        tr.appendChild(td);
        this.groups[this.groupOnFocus].push(tr);
        this.tbody.appendChild(tr);
    }
    sort(asc=true){
        let rows = this.groups[this.groupOnFocus] || null; // Carrega todas as linhas do grupo em foco
        if(!rows || rows.length == 0){ return null } // Se tabela for fazia, nao executa processo para classificar
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
            if(!this.__validateForm()){dotAlert('danger', '<b>Erro:</b> Chave duplicada ou vazia, corrija antes de prosseguir'); return false;}
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
    loadSchema(){
        this.editingSchema = true;
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
        cancel.onclick = () => this.__cancelChangeSchema();
        this.controlsContainer.appendChild(btnSaveSchema);
        this.controlsContainer.appendChild(cancel);
        for(let field in this.schema){
            let tr = document.createElement('tr');
            let th = document.createElement('th');
            th.classList = this.keyClassList;
            th.innerHTML = field;
            let td = document.createElement('td');
            td.classList = this.valueClassList;
            let attrs = this.schema[field.replace(' ', '_')].split(';');
            attrs = attrs.filter((e)=>{return e != ''})
            let size = attrs.length;
            for(let i = 0; i < size; i++){
                let label_text = `<span class="label-name bg-dark text-white user-select-none">${attrs[i].split('=')[0]}</span><span style="display: none;">=</span><span class="label-status bg-warning cursor-text" contenteditable="true">${attrs[i].split('=')[1]}</span>`;
                let label = document.createElement('label');
                label.classList = 'label opacity-75';
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
        label.classList = 'label' ;
        label.innerHTML = '<span class="label-name bg-success text-white" contenteditable="true">key</span><span style="display: none;">=</span><span class="label-status bg-warning" contenteditable="true">value</span>';
        label.ondblclick = (e) => {if(e.ctrlKey){e.preventDefault();label.remove();}};
        target.before(label);
    }
    __saveSchema(){
        let trs = this.tbody.querySelectorAll('tr');
        let size = trs.length;
        for(let i = 0; i < size; i++){ // Salva no dicionario schema dados ajustados
            let labels = [];
            trs[i].querySelectorAll('.label').forEach((e)=>{
                if(e.textContent != '='){labels.push(e.textContent)}
            });
            let key = trs[i].querySelector('th').innerText;
            this.schema[key] = labels.join(';')
        }
        document.querySelectorAll('[data-type=btnSaveSchema],[data-type=cancelSchemaBtn]').forEach((e) => e.remove()); // Remove os botoes para gravar e cancelar schema
        this.groupsMenu.classList.remove('d-none'); // Reexibe os botoes do form
        this.controls.classList.remove('d-none'); // Reexibe o menu dos grupos
        this.groupFocus(this.groupOnFocus); // Reexibe
        this.editingSchema = false;
    }
    __cancelChangeSchema(){
        this.tbody.innerHTML = '';
        this.groups[this.groupOnFocus].forEach(e => {this.tbody.appendChild(e)}); // Monta no tbody as tr do grupo em foco 
        document.querySelectorAll('[data-type=btnSaveSchema],[data-type=cancelSchemaBtn]').forEach((e) => e.remove()); // Remove os botoes para gravar e cancelar schema
        this.groupsMenu.classList.remove('d-none'); // Reexibe os botoes do form
        this.controls.classList.remove('d-none'); // Reexibe o menu dos grupos
        this.editingSchema = false;
    }
    __deleteRow(tr){
        let key = tr.querySelector('th').innerText;
        let schema_index = key.replace(' ', '_');
        try{delete this.schema[schema_index]}catch(e){} // Tenta apagar schema (caso exista)
        tr.setAttribute('to_delete', 'true');
        tr.remove();
        let size = this.groups[this.groupOnFocus].length;
        for(let i = 0; i < size; i++){
            let to_delete = false;
            try{
                if(this.groups[this.groupOnFocus][i].getAttribute('to_delete') == 'true'){to_delete = true;}
            }catch(e){}
            if(to_delete){this.groups[this.groupOnFocus].splice(i, 1)}            
        }
    }
    getJson(){
        let result_json = [];
        for(let grupo in this.groups){
            for(let row in this.groups[grupo]){
                let tr = this.groups[grupo][row];
                let th = tr.querySelector('th');
                let td = tr.querySelector('td'); // Busca o campo de valor (que contem todos atributos do json)
                let json_item = {name:th.innerText, value:td.innerText};
                if(td.dataset.type != 'newRow'){ // Carrega schema se nao for newRow
                    let schema = this.schema[th.dataset.originalname.replace(' ', '_')];
                    json_item = this.__addSchema(json_item, schema);
                }
                result_json.push(json_item); // Insere campo formatado no array json
            }
        }
        return result_json;
    }
    __addSchema(field, schema){ // Funcao (private) que adiciona os demais atributos ao field
        let fields = schema.split(';');
        let size = fields.length;
        for(let i = 0; i < size; i++){
            let [key, value] = fields[i].split('=');
            field[key] = value;
        }
        return field;
    }
    exportJson(e){
        let data = JSON.stringify(this.getJson());
        let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(data);
        let filename = 'form.json';
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
        for(let grupo in this.groups){
            let size = this.groups[grupo].length;
            for(let i = 0; i < size; i++){
                let tr = this.groups[grupo][i];
                let key = tr.querySelector('th').innerText;
                if(!this.enableDuplicates && key_names.includes(key)){ // Valida se viagem nao eh duplicada
                    tr.classList.add('table-danger');
                    has_errors = true;
                }
                else if(key.trim() == ''){ // Valida se key eh vazia
                    tr.classList.add('table-danger');
                    has_errors = true;
                }
                else{
                    key_names.push(key);
                    tr.classList.remove('table-danger');
                }
            }
        }
        return has_errors ? false : true;
    }
    cleanForm(){
        this.tbody.innerHTML = '';
        this.groups = {};
        this.schema = {};
    }
    
}