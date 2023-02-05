/*
* jsSelectm   Implementa controle para select multiple
*
* @version  1.00
* @since    03/02/2023
* @release  03/02/2023 []
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com}
* @depend   boostrap 5.2.0, fontawesome 5.15.4, dot.css, dot.js
*/
class jsSelectm{
    constructor(el, options){
        this.target = el;
        // Configuracoes
        this.optionsSelected = options?.optionsSelected || []; // Opcoes pre selecionadas ao instanciar objeto
        this.options = options?.options || this.__initializeOptions();
        this.groups = options?.groups || false; // Informa grupo para os select
        this.title = options?.title || false; // Titulo do select (opcional)
        this.customStyles = options?.customStyles != undefined ? options.customStyles : false; // Se false criar estilos
        // Estilizacao
        this.wrapperClassList = options?.wrapperClassList || 'jsSelectm_wrapper'; // Classes o titulo (small) do select 
        this.iconUncheckedClasslist = options?.iconUncheckedClasslist || 'far fa-square fa-fw'; // Classes do icone desmarcado
        this.iconCheckedClasslist = options?.iconCheckedClasslist || 'far fa-check-square fa-fw'; // Classes do icone marcado
        this.emptySelectMessage = options?.emptySelectMessage || '<p class="text-muted">Nenhuma opção disponivel</p>'; // Mensagem exibida em caso de select vazio
        this.onchange = options?.onchange != undefined ? options.onchange : () => {}; // Funcao a ser chamada ao alterar componente
        this.reorderOptions = options?.reorderOptions != undefined ? options.reorderOptions : true; // Se sim reordena opcoes baseado no innerText
        this.disabled = options?.disabled != undefined ? options.disabled : false; // Se sim desativa operacoes nos eventos click e altera formatacao

        this.__buildSelect();
        if(!this.customStyles){this.__addStyles();} // Cria estilos padrao caso nao definido estilos customizados
        this.buildOptions();
    }
    __addStyles(){
        let style = document.createElement('style');
        style.innerHTML = '.jsSelectm_wrapper{border: 1px solid #ced4da;border-radius: 0.375rem;padding: 0.375rem 0.875rem 0.475rem 0.75rem;}';
        style.innerHTML += '.jsSelectm_wrapper.disabled{background-color: #E9ECEF;}';
        style.innerHTML += '.jsSelectm_wrapper:focus-within{border-color: #86b7fe;outline: 0;box-shadow: 0 0 0 0.25rem rgb(13 110 253 / 25%);}';
        style.innerHTML += '.jsSelectm_wrapper small{display: block; margin-bottom: 5px;}';
        style.innerHTML += '.jsSelectm_wrapper > div{max-height:230px;overflow-y: scroll;}';
        style.innerHTML += '.jsSelectm_wrapper li{background-color: aqua;}';
        style.innerHTML += '.jsSelectm_wrapper div[data-value]{padding: 2px 5px 2px 5px; border-radius: 3px;}';
        style.innerHTML += '.jsSelectm_wrapper div[data-select]{background-color: rgba(25, 135, 84, 0.25)!important;}';
        if(!this.disabled){style.innerHTML += '@media(min-width: 992px){.jsSelectm_wrapper div[data-value]:hover{cursor: pointer;background-color: #ced4da; opacity: 0.5;}}';}
        document.getElementsByTagName('head')[0].appendChild(style);
    }
    __buildSelect(){
        this.target.style.display = 'none'; // Oculta select original
        this.wrapper = document.createElement('div');this.wrapper.classList = this.wrapperClassList;
        if(this.disabled){this.wrapper.classList.add('disabled')}
        if(this.title){
            this.titleEl = document.createElement('small');this.titleEl.innerHTML = this.title;
            this.wrapper.appendChild(this.titleEl);
        }
        this.optionsContainer = document.createElement('div');this.optionsContainer.style.marginTop = '5px';
        this.wrapper.appendChild(this.optionsContainer);
        this.target.after(this.wrapper);
    }
    __initializeOptions(){
        let options = {};
        this.target.querySelectorAll('option').forEach((e) => {
            options[e.value] = `${e.innerText}`;
            if(e.selected){
                this.optionsSelected.push(String(e.value));
            }
        });
        return options;
    }
    __reorderOptions(){
        let items = [...this.optionsContainer.querySelectorAll('[data-value]')];
        let reordered = items.sort(function(a, b) {
            return a.innerText == b.innerText
            ? 0
            : (a.innerText > b.innerText ? 1 : -1);
        });
        this.optionsContainer.innerHTML = '';
        for(let i in reordered){
            this.optionsContainer.appendChild(reordered[i]);
        }
    }
    buildOptions(){ // Monta os options  
        this.optionsContainer.innerHTML = '';
        if(this.groups){this.__buildGroupsContainer();}
        for(let key in this.options){
            let option = document.createElement('div');
            let checkIcon = document.createElement('i');
            if(this.optionsSelected.includes(key)){
                checkIcon.classList = this.iconCheckedClasslist;
                option.dataset.select = '';
            }
            else{checkIcon.classList = this.iconUncheckedClasslist;}
            let optionTxt = document.createElement('span');
            option.dataset.value = key;
            optionTxt.innerHTML = this.options[key];
            option.appendChild(checkIcon);
            option.appendChild(optionTxt);
            if(!this.disabled){
                option.onclick = () => {
                    this.__switchOption(option);
                };
            }
            if(this.groups){this.__getGroupContainer(key).appendChild(option);} // Se trabalhando com grupos adiciona item no devido grupo
            else{this.optionsContainer.appendChild(option);} // Caso nao insere no container
        }
        if(Object.keys(this.options).length == 0){
            this.optionsContainer.innerHTML = this.emptySelectMessage;
        }
        else if(this.reorderOptions){this.__reorderOptions();}
    }
    __buildGroupsContainer(){
        let acc = document.createElement('div');acc.classList = 'accordion';acc.setAttribute('data-jsSelect-role','group_container');
        for(let i in this.groups){
            let acc_item = document.createElement('div');acc_item.classList = 'accordion-item';
            let acc_header = document.createElement('div');acc_header.classList = 'accordion-header pointer';
            let acc_button = document.createElement('span');acc_button.classList = 'accordion-button collapsed fs-6 py-2';acc_button.setAttribute('data-bs-toggle','collapse');acc_button.setAttribute('data-bs-target',`[data-group=${i}]`);
            acc_button.innerHTML = i;
            let acc_container = document.createElement('div');acc_container.classList = 'accordion-collapse collapse';acc_container.setAttribute('data-group', i);acc_container.setAttribute('data-bs-parent', '[data-jsSelect-role=group_container]');
            let acc_body = document.createElement('div');acc_body.classList = 'accordion-collapse collapse';
            acc_container.appendChild(acc_body);
            acc_header.appendChild(acc_button);
            acc_item.appendChild(acc_header);
            acc_item.appendChild(acc_container);
            acc.appendChild(acc_item);
            this.optionsContainer.appendChild(acc);
        }
    }
    __getGroupContainer(key){ // Localiza se item esta em algum grupo, se sim retorna o container do grupo, caso nao retorna o container principal
        for(let group in this.groups){
            if(this.groups[group].includes(key)){return this.optionsContainer.querySelector(`[data-group=${group}]`);}
        }
        return this.optionsContainer;
    }
    __switchOption(opt){ // Altera stilo e data-attr do option e chama funcao que refaz conteudo do select target 
        if(opt.dataset.select != undefined){
            opt.removeAttribute('data-select')
            opt.querySelector('i').classList = this.iconUncheckedClasslist;
            this.optionsSelected.splice(this.optionsSelected.indexOf(opt.dataset.value), 1);
        }
        else{
            opt.setAttribute('data-select','')
            opt.querySelector('i').classList = this.iconCheckedClasslist;
            this.optionsSelected.push(opt.dataset.value);
        }
        this.rebuildTargetOptions();
    }
    rebuildTargetOptions(){
        this.target.innerHTML = ''; // Limpa os options
        this.optionsContainer.querySelectorAll('[data-select]').forEach((e) => {
            this.target.innerHTML += `<option value="${e.dataset.value}" selected>${e.innerText}</option>`;
        })
        this.onchange();
    }
}