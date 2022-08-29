class jsForm{
    constructor(options){
        this.data = options?.data || []; // Json com dados do form
        this.container = options?.container || document.body; // parentNode do form, caso nao informado append no document.body
        this.legend = '';
        this.legendContainer = null;
        this.controls = null;
        this.groupsMenu = null;
        this.formContainer = null;
        this.form = null;
        this.tbody = null;
        this.groups = {};
        this.groupOnFocus = null;
        this.formClassList = options?.formClassList || 'table border';
        this.groupsMenuClasslist = 'col-auto';
        this.groupsMenuStyle = 'min-width: 180px;';
        this.canSave = options?.canSave != undefined ? options.canSave : true;
        this.canDownloadJson = options?.canDownloadJson != undefined ? options.canDownloadJson : true;
        this.saveBtn = null;
        this.jsonBtn = null;
        this.save = options?.save != undefined ? options.save : function(){console.log('jsForm: Nenhuma funcao definida para save, nas opcoes marque {canSave:true, save: suaFuncao} ')}; // Funcao definida aqui sera acionada no evento click do botao save
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
        this.groupFocus(group); // Exibe grupo
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
        let controlsContainer = document.createElement('div'); // Col para controles (flex item)
        controlsContainer.classList = 'col-auto';
        this.controls = document.createElement('div'); // Div para grupo de botoes (btn-group)
        this.controls.classList = 'btn-group';
        if(this.canSave){
          this.saveBtn = document.createElement('button');
          this.saveBtn.classList = 'btn btn-sm btn-secondary px-3';
          this.saveBtn.innerHTML = '<i class="fas fa-save"></i>';
          this.saveBtn.onclick = () => this.save();
          this.controls.appendChild(this.saveBtn);
        }
        if(this.canDownloadJson){
          this.jsonBtn = document.createElement('button');
          this.jsonBtn.classList = 'btn btn-sm btn-secondary';
          this.jsonBtn.innerHTML = '<i class="fas fa-download me-2"></i> JSON';
          this.controls.appendChild(this.jsonBtn);
        }
        controlsContainer.appendChild(this.controls);
        row.appendChild(this.legendContainer);
        row.appendChild(controlsContainer);
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
        }
        for(let item in this.data){ // Percorre todas as linhas alocando cada registro no respectivo grupo
            let tr = document.createElement('tr');
            let th = document.createElement('th');
            th.classList = this.keyClassList;
            th.innerHTML = this.data[item].name;
            let td = document.createElement('td');
            for(let attr in this.data[item]){td.setAttribute(attr, this.data[item][attr]);}
            td.classList = this.valueClassList;
            td.contentEditable = true;
            td.innerHTML = this.data[item].value;
            tr.appendChild(th);
            tr.appendChild(td);
            if(this.data[item].group == undefined){ // Se nao existe grupo associado adicona linha no grupo Geral
                if('Geral' in this.groups){this.groups.Geral.push(tr)}
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
    }
    groupFocus(group){ // Carrega campos do respectivo grupo no form
        this.tbody.innerHTML = '';
        this.groupOnFocus = group;
        try{this.groupsMenu.querySelector('[data-type="group-link"].active').classList.remove('active');}catch(e){} // Caso acionado na criacao da tabela vai gerar excecao pois nao existe nenhum ativo
        this.groupsMenu.querySelector(`[data-groupname="${group}"]`).classList.add('active');
        this.groups[group].forEach(e => { this.tbody.appendChild(e)});
    }
    downloadJson(){
        for(let grupo in this.groups){
            for(let row in this.groups[grupo]){
                let tr = this.groups[grupo][row];
                let td = tr.querySelector('td');
                let attrs = td.getAttributeNames().filter((e) => {return e != 'contenteditable' && e != 'value'});
                let size = attrs.length;
                let json_item = {value:td.innerText};
                for(let i = 0; i < size; i++){
                    json_item[attrs[i]] = td.getAttribute(attrs[i]);
                }
                console.log(json_item);
            }
        }
    }
    cleanForm(){
        this.tbody.innerHTML = '';
        this.groups = {};
    }
    
}