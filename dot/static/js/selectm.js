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
            this.optionsContainer.appendChild(option);
        }
        if(Object.keys(this.options).length == 0){
            this.optionsContainer.innerHTML = this.emptySelectMessage;
        }
        else if(this.reorderOptions){this.__reorderOptions();}
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