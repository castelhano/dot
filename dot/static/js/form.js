class jsForm{
    constructor(options){
        this.data = options?.data || []; // Json com dados do form
        this.container = options?.container || document.body; // parentNode do form, caso nao informado append no document.body
        this.form = null;
        this.tbody = null;
        this.groups = {};
        this.groupOnFocus = null;
        this.formClassList = options?.formClassList || 'table border';
        this.keyClassList = options?.keyClassList || 'fit pe-5';
        this.valueClassList = options?.valueClassList || 'bg-light border';
        this.textFormEmpty = options?.textFormEmpty || 'Nada a exibir';
        
        this.createForm();
        this.buildRows();
    }
    createForm(){
        this.form = document.createElement('table');
        this.form.classList = this.formClassList;
        this.tbody = document.createElement('tbody');
        this.form.appendChild(this.tbody);
        this.container.appendChild(this.form);
    }
    buildGroupMenu(){
        let grupos = Object.keys(this.groups);
        console.log(grupos);
        // for(let i = 0; i < this.)
        // let list = `<div class="col-auto" style="min-width: 180px;"><div class="list-group" id="list-tab" role="tablist"></div></div>`;
    }
    buildRows(){
        this.cleanForm();
        if(this.data.length == 0){
            this.tbody.innerHTML = `<tr><td colspan="2" class="${this.valueClassList}">${this.textFormEmpty}</td></tr>`
        }
        for(let item in this.data){ // Percorre todas as linhas alocando cada registro no respectivo grupo
            let tr = document.createElement('tr');
            for(let attr in this.data[item]){tr.setAttribute(attr, this.data[item][attr]);}
            tr.innerHTML = `<th class="${this.keyClassList}">${this.data[item].name}</th><td class="${this.valueClassList}" contenteditable="true">${this.data[item].value}</td>`
            if(this.data[item].group == undefined){ // Se nao existe grupo associado adicona linha no grupo Geral
                if('Geral' in this.groups){this.groups.Geral.push(tr)}
                else{this.groups['Geral'] = [tr];} // Caso ainda nao exista registro para o grupo, insere no dicionario
            }
            else{ // Caso exista grupo, insere a linha no respectivo grupo -> this.groups
                if(this.data[item].group in this.groups){this.groups[this.data[item].group].push(tr)} // Se grupo ja tem registros faz append na tr para o grupo
                else{this.groups[this.data[item].group] = [tr];} // Caso ainda nao exista registro para o grupo, insere no dicionario
            }
        }
        let [group] = 'Geral' in this.groups ? ['Geral'] : Object.keys(this.groups); // Seleciona o grupo Geral (caso exista) ou o primeiro grupo cadastrado
        this.groupFocus(group); // Exibe grupo
    }
    loadData(data){
        this.data = data;
        this.buildRows();        
    }
    groupFocus(group){ // Carrega campos do respectivo grupo no form
        this.tbody.innerHTML = '';
        this.groupOnFocus = group;
        this.groups[group].forEach(e => { this.tbody.appendChild(e)});
    }
    cleanForm(){
        this.tbody.innerHTML = '';
        this.groups = {};
    }
    
}