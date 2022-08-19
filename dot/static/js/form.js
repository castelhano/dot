class jsForm{
    constructor(options){
        this.data = options?.data || []; // Json com dados do form
        this.container = options?.container || document.body; // parentNode do form, caso nao informado append no document.body
        this.form = null;
        this.tbody = null;
        this.groups = {};
        this.formClassList = options?.formClassList || 'table border';
        this.keyClassList = options?.keyClassList || 'text-capitalize';
        this.valueClassList = options?.valueClassList || 'bg-light border';
        
        this.createForm();
    }
    createForm(){
        this.form = document.createElement('table');
        this.form.classList = this.formClassList;
        this.tbody = document.createElement('tbody');
        for(let item in this.data){ // Percorre todas as linhas alocando cada registro no respectivo grupo
            // for(let attr in this.data[item]){
            //     console.log(attr);
            //     // f.setAttribute(attr, this.data[0].fields[field][attr]);
            // }

            let row = `<tr><th class="${this.keyClassList}">${this.data[item].name}</th><td class="${this.valueClassList}" contenteditable="true">${this.data[item].value}</td></tr>`
            this.tbody.innerHTML += row;            
        }
        this.form.appendChild(this.tbody);
        this.container.appendChild(this.form);
    }    
    
}