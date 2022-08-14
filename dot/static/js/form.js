let obj = [
    {
        "action":"foo_fei",
        "method":"post",
        "autocomplete":"off",
        "fields": {
            "csrfmiddlewaretoken":{
                "type":"hidden",
                "name":"csrfmiddlewaretoken",
                "id":"id_csrfmiddlewaretoken",
                "value":""
            },
            "Age":{
                "name": "age",
                "id": "id_age",
                "value": "22",
                "class": "form-control",
                "type": "number",
                "min": "1",
                "max": "35",
                "data-type":"primary-key"
            },
            "Owner":{
                "name": "owner",
                "id": "id_owner",
                "value": "Rafael",
                "class": "form-control",
                "type": "text",
                "autofocus": "autofocus",
                "onclick":"console.log('fooo')"
            }
        }
    }
]
class jsForm{
    constructor(options){
        this.data = options?.data || []; // Json com dados do form
        this.container = options?.container || document.body; // parentNode do form, caso nao informado append no document.body

        this.createForm();
    }
    createForm(){
        let form = document.createElement('form');
        for(let item in this.data[0]){if(item != 'fields'){form.setAttribute(item, this.data[0][item]);}} // Monta composicao basica do form

        for(let field in this.data[0].fields){
            let f = document.createElement('input');
            for(let attr in this.data[0].fields[field]){
                f.setAttribute(attr, this.data[0].fields[field][attr]);
            }
            if(f.type != 'hidden'){form.appendChild(this.buildFormRow(f));}
            else{form.appendChild(f)}

        }
        
        
        this.container.appendChild(form);
    }
    buildFormRow(input){
        let label = document.createElement('label');
        label.setAttribute('for', input?.id || '');
        label.classList = 'col-sm-2 col-form-label text-capitalize';
        label.innerHTML = input.name;
        let input_container = document.createElement('div');
        input_container.classList = 'col-sm-10';
        input_container.appendChild(input);
        let row = document.createElement('div');
        row.classList = 'row mb-1';
        row.appendChild(label);
        row.appendChild(input_container);
        return row;
    }
    

}

