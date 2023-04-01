/*
* jsKanban   Implementa componente Kanban
*
* @version  1.2
* @since    18/09/2022
* @release  19/09/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @depend   boostrap 5.2.0, fontawesome 5.15.4, SortableJS, dot.css, dot.js
* @see      {https://github.com/SortableJS/Sortable}
*/
class jsKanban{
    constructor(options){
        // Variaveis internas
        this.kanban = null; // container pai, contem todos os boards
        this.header = null; // container dos headers (id, pesquisa, etc)
        this.controls = null; // ul com controles do kanban
        this.kanbanSelect = null; // ul com lista dos kanbans
        this.body = null; // container do corpo do kanban (boards)
        this.nav = null; // nav para filtro e navegacao das tasks
        this.restoreButton = null; // aponta para botao de restorBoard
        this.trash = []; // armazena bords deletados
        this.tags = {}; // armazena as tags cadastradas
        this.currentKanban = null; // armazena o indice do kanban em exibicao
        this.saveBtn = null; // Aponta para o botao save
        this.jsonBtn = null; // Aponta para o botao export
        this.loadBtn = null; // Aponta para o botao load
        this.searchInput = null; // Aponta para o search field
        this.modalKanban = null; // aponta para modal para editar ID do kanban (ou adicionar novo kanban)
        this.modalTask = null; // aponta para modal com dados detalhados da task
        this.modalTaskAction = null; // aponta para o botao gravar do modal de edicao da task
        this.modalKanbanCleanTasks = null; // aponta para modal para limpar tasks do kanban em exibicao
        this.modalTaskTarget = null; // aponta para a task que esta sendo editada
        this.modalDeleteComponent = null; // aponta para instancia (bootstrap modal) do modal para deletar task
        // Configuracao
        this.data = options?.data || {}; // Json com dados dos boards kanban
        this.container = options?.container || document.body; // parentNode do kanban, create(), caso nao informado append no body
        this.dndBoardsOptions = options?.dndBoardsOptions || {group:'boards',animation:100, delay: 80, delayOnTouchOnly: true}; // options da instancia Sortable JS dos boards
        this.dndTasksOptions = options?.dndTasksOptions || {group:'tasks', delay: 80, delayOnTouchOnly: true}; // options da instancia Sortable JS das tasks
        this.readOnly = options?.readOnly != undefined ? options.readOnly : false; // Boolean, se setado para true desativa todas as opcoes de edicao do kanban
        this.canSave = options?.canSave != undefined ? options.canSave : false; // Boolean, exibe/oculta controle para salvar
        this.save = options?.save != undefined ? options.save : function(){console.log('kanban: Nenhuma funcao definida para save, nas opcoes marque {canSave:true, save: suaFuncao} ')}; // Funcao definida aqui sera acionada no evento click do botao save
        this.canAddBoard = options?.canAddBoard != undefined ? options.canAddBoard : true; // Boolean, exibe/oculta controle para novo board
        this.canDeleteBoard = options?.canDeleteBoard != undefined ? options.canDeleteBoard : true; // Boolean, exibe/oculta controle para deletar board
        this.canAddTask = options?.canAddTask != undefined ? options.canAddTask : true; // Boolean, exibe/oculta controle para nova task no grupo
        this.canDeleteTask = options?.canDeleteTask != undefined ? options.canDeleteTask : true; // Boolean, exibe/oculta controle para deletar task
        this.canAddTag = options?.canAddTag != undefined ? options.canAddTag : true; // Boolean, exibe/oculta controle para nova tag
        this.showCleanKanbanBtn = options?.showCleanKanbanBtn != undefined ? options.showCleanKanbanBtn : true; // Boolean, exibe/oculta controle para limpar tasks kanban em ebibicao
        this.canDeleteTag = options?.canDeleteTag != undefined ? options.canDeleteTag : true; // Boolean, exibe/oculta controle para deletar tag
        this.canLoadFile = options?.canLoadFile != undefined ? options.canLoadFile : true; // Boolean, exibe/oculta controle para abrir arquivo com kanban
        this.canExportJson = options?.canExportJson != undefined ? options.canExportJson : true; // Boolean, exibe/oculta controle para exportar json
        // Estilizacao
        this.kanbanClasslist = options?.kanbanClasslist || 'row'; // classlist para o container principal
        this.headerClasslist = options?.headerClasslist || 'col-12 p-2'; // classlist para o header container
        // this.navContainerClasslist = options?.navContainerClasslist || 'd-none d-md-block col-auto bg-light text-muted border rounded pt-3 ps-2 fs-7 position-relative'; // classlist para o nav container
        this.navContainerClasslist = options?.navContainerClasslist || 'col-lg-auto collapse navCollapse bg-light text-muted border rounded pt-1 pt-lg-3 fs-7 position-relative'; // classlist para o nav container
        this.navClasslist = options?.navClasslist || 'list-unstyled navCollapse'; // classlist para o nav (ul)
        this.sortableClasslist = options?.sortableClasslist || 'pb-5'; // classlist para o div drag and drop
        this.bodyContainerClasslist = options?.bodyContainerClasslist || 'col-lg'; // classlist para o body container
        this.bodyClasslist = options?.bodyClasslist || 'row'; // classlist para o container flex dos boards
        this.boardClasslist = options?.boardClasslist || 'col-md-6 col-lg-4 col-xl-3'; // classlist para o board
        this.taskClasslist = options?.taskClasslist || 'callout mb-2 container-fluid'; // classlist base para as tasks

        this.create();
        this.__configureCssClass();
        this.buildControls();
        this.buildNav();
        if(!this.readOnly){this.__buildModals();}
        if(Object.keys(this.data).length > 0){this.__loadData();} // Se kanban existente, carrega estrutura
        else{this.startFromScratch()}
    }
    create(){
        this.kanban = document.createElement('div'); // Row que engloba todo o kanban
        this.kanban.classList = this.kanbanClasslist;
        this.header = document.createElement('div'); // Col, container para os headers
        this.header.classList = this.headerClasslist;
        this.nav = document.createElement('div');this.nav.id = 'kanbanNavContainer'; // Col, container para o menu de navegacao das tasks
        this.nav.classList = this.navContainerClasslist;
        let bodyCol = document.createElement('div'); // Col, container para o this.body
        bodyCol.classList = this.bodyContainerClasslist;
        this.body = document.createElement('div'); // Row que agrupa os boards 
        this.body.classList = this.bodyClasslist;
        if(!this.readOnly){
            new Sortable(this.body,this.dndBoardsOptions);
        }
        // --------------------------------
        bodyCol.appendChild(this.body);
        this.kanban.appendChild(this.header);
        this.kanban.appendChild(this.nav);
        this.kanban.appendChild(bodyCol);
        this.container.appendChild(this.kanban);
    }
    __configureCssClass(){
        let style = document.createElement('style');
        style.innerHTML = '@media(min-width: 992px){.navCollapse{min-width: 204px;min-height: 400px; display: block!important;}}';
        document.getElementsByTagName('head')[0].appendChild(style);
    }
    buildControls(){
        let row = document.createElement('div');row.classList = 'row g-1';
        let colStart = document.createElement('div');colStart.classList = 'col-auto order-1';
        let colCenter = document.createElement('div');colCenter.classList = 'col-md order-3 order-md-2';
        let colEnd = document.createElement('div');colEnd.classList = 'col-auto ms-auto order-2 order-md-3';
        let collapseBtn = document.createElement('a');collapseBtn.classList = 'btn btn-sm btn-outline-secondary d-inline-block d-lg-none me-1';collapseBtn.innerHTML = '<i class="fas fa-filter"></i>';collapseBtn.setAttribute('data-bs-toggle', 'collapse');collapseBtn.href = '#kanbanNavContainer';
        colStart.appendChild(collapseBtn);
        let btnGroup = document.createElement('div');btnGroup.classList = 'btn-group';
        let selectKanbanContainer = document.createElement('div');selectKanbanContainer.classList = 'btn-group d-inline-block me-1';
        this.kanbanModalBtn = document.createElement('button');this.kanbanModalBtn.classList = 'btn btn-sm btn-primary';this.kanbanModalBtn.innerHTML = 'Sem nome';
        let kanbanDropdownLink = document.createElement('button');kanbanDropdownLink.classList = 'btn btn-sm btn-primary dropdown-toggle dropdown-toggle-split';kanbanDropdownLink.setAttribute('data-bs-toggle','dropdown');
        this.kanbanSelect = document.createElement('ul');this.kanbanSelect.classList = 'dropdown-menu fs-8';
        let divider = document.createElement('hr');divider.classList = 'dropdown-divider';divider.setAttribute('data-type', 'selectKanbanDivider');
        this.kanbanSelect.appendChild(divider);
        if(!this.readOnly){
            this.kanbanModalBtn.onclick = () => {
                let input = document.getElementById('kanbanModalId');
                input.value = this.kanbanModalBtn.innerText;
                this.modalKanban._element.querySelector('[data-type="modalExtra"]').classList.remove('d-none'); // Exibe o botao de excluir ao inserir novo kanban
                this.modalKanban._element.querySelector('[data-type="modalAction"]').onclick = () => {
                    if(input.value == ''){
                        input.value = 'Obrigatorio..';
                        input.focus();
                    }
                    else{
                        this.data.kanbans[this.currentKanban].id = input.value;
                        this.kanbanSelect.querySelector(`[data-kanban="${this.currentKanban}"]`).innerHTML = input.value;
                        this.kanbanModalBtn.innerHTML = input.value;
                        this.modalKanban.hide();
                    }
                }
                this.modalKanban._element.querySelector('[data-type="modalExtra"]').onclick = () => {
                    this.modalKanban.hide();
                    this.modalDeleteComponent._element.querySelector('[data-type="modalAction"]').onclick = () => {
                        if(this.data.kanbans.length > 1){ // Se existe mais de um kanban, apaga o current e exibe o novo posicao 0
                            this.data.kanbans.splice(this.currentKanban, 1);
                            this.currentKanban = 0;
                        }
                        else{ // So existe um kanban, apenas limpa registros 
                            this.data.kanbans[this.currentKanban] = {
                                id: 'Sem nome',
                                boards: [],
                                tags: []
                            };
                        }
                        this.__loadData(); // Refaz select kanban, tags e exibe kanban ajustado
                        this.modalDeleteComponent.hide();
                    }
                    this.modalDeleteComponent.show();
                }
                this.modalKanban.show(); // Exibe modal para alterar nome kanban
                setTimeout(function() {input.select();}, 470); // Move o foco para o input
            }
            let newKanbanLink = document.createElement('li');newKanbanLink.classList = 'dropdown-item dropdown-item-success pointer';newKanbanLink.innerHTML = '<i class="fas fa-plus me-1"></i> Novo';
            newKanbanLink.onclick = () => {
                let input = document.getElementById('kanbanModalId');
                input.value = '';
                this.modalKanban._element.querySelector('[data-type="modalExtra"]').classList.add('d-none'); // Oculta o botao de excluir ao inserir novo kanban
                this.modalKanban._element.querySelector('[data-type="modalAction"]').onclick = () => {
                    if(input.value == ''){
                        input.value = 'Obrigatorio..';
                        input.focus();
                    }
                    else{
                        this.dataSaveCurrent(); // Salva atual antes de mover para o novo
                        let nextKanbanIndex = this.data.kanbans.length; // Verifica o indice do novo kanban
                        this.data.kanbans.push({ // Insere o novo kanban
                            id : input.value,
                            tags : [],
                            boards : []
                        });
                        this.currentKanban = nextKanbanIndex; // Aponta para o novo kanban
                        // Cria link no select para o novo kanban
                        let kanbanLink = document.createElement('li');kanbanLink.classList = 'dropdown-item pointer';kanbanLink.setAttribute('data-type', 'kanbanLink');kanbanLink.setAttribute('data-kanban', nextKanbanIndex);kanbanLink.innerHTML = input.value;
                        kanbanLink.onclick = () => {
                            this.dataSaveCurrent(); // Salva no objeto data os kabnbans e demais elementos
                            this.currentKanban = nextKanbanIndex; // Aponta para o novo kanban
                            this.__showKanban(); // Exibe o kanban
                        }
                        this.kanbanSelect.querySelector('[data-type="selectKanbanDivider"]').before(kanbanLink);
                        // TODO: Reordenar o select kanban em ordem alfabetica
                        this.__showKanban();
                        this.modalKanban.hide();
                    }
                }
                this.modalKanban.show(); // Exibe modal para alterar nome kanban
                setTimeout(function() {input.select();}, 470); // Move o foco para o input
            };
            this.kanbanSelect.appendChild(newKanbanLink);
            if(this.showCleanKanbanBtn){
                let cleanTasksBtn = document.createElement('li');cleanTasksBtn.classList = 'dropdown-item pointer';cleanTasksBtn.innerHTML = '<i class="fas fa-stop text-danger me-1"></i> Limpar Tasks';
                cleanTasksBtn.onclick = () => {this.modalKanbanCleanTasks.show();};
                this.kanbanSelect.appendChild(cleanTasksBtn);
            }
        }
        else{
            this.kanbanModalBtn.disabled = true;
            divider.style.display = 'none';
        }
        selectKanbanContainer.appendChild(this.kanbanModalBtn);
        selectKanbanContainer.appendChild(kanbanDropdownLink);
        selectKanbanContainer.appendChild(this.kanbanSelect);
        colStart.appendChild(selectKanbanContainer);
        if(this.canAddBoard && !this.readOnly){
            let addBoard = document.createElement('button');
            addBoard.classList = 'btn btn-sm btn-success'
            addBoard.innerHTML = '<i class="fas fa-plus me-md-2"></i><span class="d-none d-md-inline">Board</span>'
            addBoard.onclick = () => this.addBoard();
            btnGroup.appendChild(addBoard);
        }
        if(this.canDeleteBoard && !this.readOnly){
            this.restoreButton = document.createElement('button');
            this.restoreButton.classList = 'btn btn-sm btn-outline-secondary';
            this.restoreButton.innerHTML = '<i class="fas fa-history"></i>';
            this.restoreButton.disabled = true;
            this.restoreButton.onclick = () => this.restoreLastBoard();
            btnGroup.appendChild(this.restoreButton);
        }
        colStart.appendChild(btnGroup);
        // ---
        this.searchInput = document.createElement('input');this.searchInput.type = 'search';this.searchInput.classList = 'form-control form-control-sm';
        this.searchInput.placeholder = 'Pesquisa..';
        this.searchInput.oninput = () => this.filter(this.searchInput.value);
        colCenter.appendChild(this.searchInput);
        // ---
        let btnGroup2 = document.createElement('div');btnGroup2.classList = 'btn-group';
        if(this.canSave && !this.readOnly){
            this.saveBtn = document.createElement('button');this.saveBtn.classList = 'btn btn-sm btn-success';this.saveBtn.innerHTML = '<i class="fas fa-save fa-fw"></i>';
            this.saveBtn.onclick = () => this.save();
            btnGroup2.appendChild(this.saveBtn);
        }
        if(this.canLoadFile){
            this.loadBtn = document.createElement('button');this.loadBtn.classList = 'btn btn-sm btn-primary';this.loadBtn.innerHTML = '<i class="fas fa-upload fa-fw me-0"></i>';
            this.loadBtn.onclick = () => {
                let loadInput = document.createElement('input');loadInput.type = 'file';loadInput.setAttribute('accept', '.json');loadInput.style.display = 'none';
                let obj = this;
                loadInput.onchange = () => {
                    let fr = new FileReader();
                    fr.onload = (function(){
                        obj.data = JSON.parse(fr.result);
                        obj.__loadData(0);
                    });
                    fr.readAsText(loadInput.files[0]);
                }
                loadInput.click();
            };
            btnGroup2.appendChild(this.loadBtn);
        }
        if(this.canExportJson && !this.readOnly){
            this.jsonBtn = document.createElement('button');this.jsonBtn.classList = 'btn btn-sm btn-secondary';this.jsonBtn.innerHTML = '<i class="fas fa-download me-md-2"></i><span class="d-none d-md-inline">JSON</span>';
            this.jsonBtn.onclick = (e) => this.exportJson(e);
            btnGroup2.appendChild(this.jsonBtn);
        }
        colEnd.appendChild(btnGroup2);        
        // ---
        row.appendChild(colStart);
        row.appendChild(colCenter);
        row.appendChild(colEnd);
        this.header.appendChild(row);

    }
    __controlsBuildSelectKanban(){
        this.kanbanSelect.querySelector()
    }
    buildNav(){
        let cleanFilter = document.createElement('span');
        cleanFilter.setAttribute('data-type', 'navCleanFilter');
        cleanFilter.classList = 'pointer text-primary position-absolute fs-8 d-none';
        cleanFilter.style.top = '3px';
        cleanFilter.style.right = '10px';
        cleanFilter.innerHTML = `Limpar`;
        cleanFilter.onclick = () => this.cleanFilters();
        this.nav.appendChild(cleanFilter);
        let menu = document.createElement('ul');menu.classList = this.navClasslist;
        this.__navReorderTags(); // Insere as tags no nav de e reordena pelo nome
        let addTag = document.createElement('li');
        addTag.setAttribute('data-type', 'navNewTag');
        addTag.innerHTML = `<i class="fas fa-plus fa-fw"></i>Nova tag`;
        if(this.canAddTag && !this.readOnly){
            addTag.classList = 'pointer mt-2';
            addTag.onclick = () => {this.__navTagForm()};
        }
        menu.appendChild(addTag);
        if(this.canDeleteTag && !this.readOnly){
            let deleteTag = document.createElement('li');
            deleteTag.setAttribute('data-type', 'navDelTag');
            deleteTag.classList = 'pointer mt-1 text-danger';
            deleteTag.innerHTML = `<i class="fas fa-trash fa-fw"></i>Excluir Tag`;
            deleteTag.onclick = () => {
                this.nav.querySelectorAll('[data-type="kanbanNavTagFormControl"], [data-type="kanbanNavTagFormHelp"]').forEach((el) => el.remove()); // Apaga form 'antigo' caso tentativa de gerar form duplicado
                if(Object.keys(this.tags).length == 0){ // Se nao existir tags cadastradas, exibe alerta e nao da sequencia no codigo
                    let msgAlert = document.createElement('div');msgAlert.classList = 'mt-2';msgAlert.setAttribute('data-type', 'kanbanNavTagFormHelp');
                    msgAlert.innerHTML = '<i class="fas fa-info text-primary me-2"></i>Nenhuma tag cadastrada';
                    deleteTag.after(msgAlert);
                    return false;
                }
                let inputGroup = document.createElement('div');inputGroup.classList = 'input-group mt-1';inputGroup.setAttribute('data-type', 'kanbanNavTagFormControl');
                let select = document.createElement('select');select.classList = 'form-select form-select-sm';
                for(let tag in this.tags){
                    select.innerHTML += `<option value="${tag}">${this.tags[tag].text}</option>`;
                }
                let deleteBtn = document.createElement('button');deleteBtn.classList = 'btn btn-sm btn-danger';deleteBtn.style.width = '35px';deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
                deleteBtn.onclick = () => {
                    this.body.querySelectorAll(`[data-tag="${select.options[select.selectedIndex].innerHTML}"]`).forEach((el) => el.remove()); // Remove a tag das taks ja inseridas
                    delete this.tags[select.value]; // Apaga a tag do dicionario de tags
                    this.__navReorderTags(); // Ajusta exibicao das tags no nav
                    inputGroup.remove();msgAlert.remove(); // Remove o inputgroup e msgalert
                }
                let cancelBtn = document.createElement('button');cancelBtn.classList = 'btn btn-sm btn-secondary';cancelBtn.style.width = '32px';cancelBtn.innerHTML = '<i class="fas fa-undo"></i>';
                let msgAlert = document.createElement('span');msgAlert.setAttribute('data-type', 'kanbanNavTagFormHelp');
                msgAlert.innerHTML = '<b class="text-danger">Atenção</b> não pode ser desfeito';
                cancelBtn.onclick = () => {inputGroup.remove();msgAlert.remove()};
                inputGroup.appendChild(select);
                inputGroup.appendChild(deleteBtn);
                inputGroup.appendChild(cancelBtn);
                deleteTag.after(inputGroup);
                inputGroup.after(msgAlert);
            };
            menu.appendChild(deleteTag);
        }
        // -----------
        let divider = document.createElement('hr');divider.classList = 'my-3';
        let vencidosLink = document.createElement('li');vencidosLink.classList = 'pointer user-select-none mb-1';vencidosLink.setAttribute('data-type', 'navFilter');vencidosLink.setAttribute('data-filter', 'vencidos');vencidosLink.innerHTML = '<i class="fas fa-calendar-alt fa-fw"></i>Vencidos <sup>0</sup>';
        vencidosLink.onclick = () => {
            this.cleanFilters();
            this.nav.querySelector('[data-type="navCleanFilter"]').classList.remove('d-none');
            vencidosLink.classList.add('fw-bold', 'text-primary');
            let hoje = dateToday({native:true});
            let tasks = this.body.querySelectorAll('.callout').forEach((el) => {
                if(el.dataset?.termino && el.dataset.termino < hoje && parseInt(el.dataset?.progresso || 0) < 100){}
                else{el.classList.add('d-none')}
            });
        };
        let semPrazoLink = document.createElement('li');semPrazoLink.classList = 'pointer user-select-none mb-1';semPrazoLink.setAttribute('data-type', 'navFilter');semPrazoLink.setAttribute('data-filter', 'semPrazo');semPrazoLink.innerHTML = '<i class="fas fa-calendar fa-fw"></i>Sem prazo <sup>0</sup>';
        semPrazoLink.onclick = () => {
            this.cleanFilters();
            this.nav.querySelector('[data-type="navCleanFilter"]').classList.remove('d-none');
            semPrazoLink.classList.add('fw-bold', 'text-primary');
            let tasks = this.body.querySelectorAll('.callout').forEach((el) => {
                const inicioValid = el.dataset?.inicio && el.dataset.inicio != '';
                const terminoValid = el.dataset?.termino && el.dataset.termino != '';
                if(inicioValid && terminoValid){el.classList.add('d-none')}
            });
        };
        menu.appendChild(divider);
        menu.appendChild(vencidosLink);
        menu.appendChild(semPrazoLink);
        this.nav.appendChild(menu);
    }
    __navTagForm(tag=null){ // Monta form para adicionar ou editar tag
        this.nav.querySelectorAll('[data-type="kanbanNavTagFormControl"], [data-type="kanbanNavTagFormHelp"]').forEach((el) => el.remove()); // Apaga form 'antigo' caso tentativa de gerar form duplicado
        let inputGroup = document.createElement('div');inputGroup.classList = 'input-group mt-1';inputGroup.setAttribute('data-type', 'kanbanNavTagFormControl');
        let bgColorBtn = document.createElement('input');bgColorBtn.type = 'color';bgColorBtn.classList = 'form-control form-control-sm';bgColorBtn.style.maxWidth = '50px';bgColorBtn.title = 'Cor do fundo';
        let colorBtn = document.createElement('input');colorBtn.type = 'color';colorBtn.classList = 'form-control form-control-sm';colorBtn.style.maxWidth = '50px';colorBtn.value = '#ffffff';colorBtn.title = 'Cor do texto';
        let input = document.createElement('input');input.type = 'text';input.classList = 'form-control form-control-sm fs-8';
        let checkContainer = document.createElement('div');checkContainer.classList = 'form-check mt-2';checkContainer.setAttribute('data-type', 'kanbanNavTagFormControl');
        let checkbox = document.createElement('input');checkbox.type = 'checkbox'; checkbox.classList = 'form-check-input';checkbox.id = 'kanbanTagGlobalCheck';
        let checklabel = document.createElement('label');checklabel.classList = 'form-check-label';checklabel.setAttribute('for', 'kanbanTagGlobalCheck');checklabel.innerHTML = 'Tag Global';
        if(tag){
            input.value = tag.text;
            bgColorBtn.value = tag.bg;
            colorBtn.value = tag.color;
            checkbox.checked = tag.global == 'true' ? true : false;
        }
        inputGroup.appendChild(bgColorBtn);
        inputGroup.appendChild(colorBtn);
        inputGroup.appendChild(input);
        input.onkeydown = (e) => { // Implementa salvamento da tag (edicao de tag existente ou criacao de nova)
            if(e.key == 'Enter'){
                if(tag){ // Tag informada, tenta editar dados da tag
                    let currentTagText = tag.text; // Armazena a descricao da tag antes de alterada
                    if(input.value.trim() != ''){ // Caso text nao seja vazio
                        if(tag.text != input.value){ // Foi alterado nome da tag, precisa validar se nao sera duplicado
                            if(Object.values(this.tags).some(el => el.text.trim().toLowerCase() == input.value.trim().toLowerCase())){ // Valida se entrada nao eh duplicada
                                this.nav.querySelectorAll('[data-type="kanbanNavTagFormHelp"]').forEach((el) => el.remove()); // Se ja existir span com mensagem, apaga o elemento
                                let msgAlert = document.createElement('div');msgAlert.classList = 'text-danger mt-2';msgAlert.setAttribute('data-type', 'kanbanNavTagFormHelp');msgAlert.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> TAG Duplicada';
                                inputGroup.after(msgAlert);
                                input.value = tag.text; // Volta nome da tag para o original
                                return false;
                            }
                            tag.text = input.value.trim();
                        }
                        tag.bg = bgColorBtn.value;
                        tag.color = colorBtn.value;
                        if(checkbox.checked){tag.global = 'true'}
                        else if(tag.hasOwnProperty('global')){delete tag['global']}
                        let tags = document.querySelectorAll(`[data-tag="${currentTagText}"]`);// Busca todas as tasks com a tag editada para atualizar aparencia
                        tags.forEach((el) => { // Altera os atributos dos elementos tags
                            el.style.backgroundColor = tag.bg;
                            el.style.color = tag.color;
                            el.innerHTML = tag.text;
                            el.dataset.tag = tag.text;
                        });
                    }
                }
                else{
                    if(input.value.trim() != ''){ // So insere nova tag se definido text
                        if(Object.values(this.tags).some(el => el.text.trim().toLowerCase() == input.value.trim().toLowerCase())){ // Valida se entrada nao eh duplicada
                            this.nav.querySelectorAll('[data-type="kanbanNavTagFormHelp"]').forEach((el) => el.remove()); // Se ja existir span com mensagem, apaga o elemento
                            let msgAlert = document.createElement('div');msgAlert.classList = 'text-danger mt-2';msgAlert.setAttribute('data-type', 'kanbanNavTagFormHelp');msgAlert.innerHTML = '<i class="fas fa-exclamation-triangle me-1"></i> TAG Duplicada';
                            inputGroup.after(msgAlert);
                            return false;
                        }
                        let newTag = {text: input.value.trim(),bg: bgColorBtn.value,color: colorBtn.value};
                        if(checkbox.checked){newTag.global = 'true'};
                        let position = Object.keys(this.tags).length;
                        this.tags[position] = newTag;
                    }
                }
                this.__navReorderTags(); // Cria a tag (elemento HTML) e reordena pelo nome
                this.nav.querySelectorAll('[data-type="kanbanNavTagFormControl"],[data-type="kanbanNavTagFormHelp"]').forEach((el) => el.remove());
            }
        };
        checkContainer.appendChild(checkbox);
        checkContainer.appendChild(checklabel);
        let newTagBtn = this.nav.querySelector('[data-type="navNewTag"]'); // Aponta para link de nova tag(ancora para inserir tags antes dele)
        newTagBtn.after(inputGroup);
        inputGroup.after(checkContainer);
        input.focus();
    }
    __navReorderTags(){
        this.cleanFilters(); // Se tiver filtro aplicado, limpa os filtros
        this.nav.querySelectorAll('[data-type="navTag"]').forEach((el)=> el.remove()); // Remove todas as tags atuais
        let newTagBtn = this.nav.querySelector('[data-type="navNewTag"]'); // Aponta para link de nova tag(ancora para inserir tags antes dele)
        let tagValues = Object.values(this.tags); // Monta array com as tags
        let orderedTags = tagValues.sort(function(a,b){return a.text > b.text ? 1 : -1}); // Reordena baseado no text da tag
        let size = orderedTags.length;
        this.tags = {}; // Limpa as tags
        for(let i = 0; i < size; i++){ // Monta dicionario reordenado e insere no nav link para as tags
            this.tags[i] = orderedTags[i]; // Insere no dicionario de tags, reordenando
            let elTag = document.createElement('li');
            elTag.setAttribute('data-type',"navTag");
            elTag.setAttribute('data-tag', orderedTags[i].text);
            let tagLabel = document.createElement('i');tagLabel.classList = `fas fa-${this.tags[i].global == 'true' ? 'tags' : 'tag'} fa-fw pointer`; tagLabel.style.color = orderedTags[i].bg;
            let tagName = document.createElement('span');tagName.classList = 'user-select-none ms-1 pointer';tagName.innerHTML = orderedTags[i].text;
            if(!this.readOnly){
                tagLabel.ondblclick = () => {
                    this.__navTagForm(this.tags[i]);
                }
            }
            tagName.onclick = () => {this.tagFilter(elTag.dataset.tag);}
            elTag.appendChild(tagLabel);
            elTag.appendChild(tagName);
            newTagBtn.before(elTag);
        }
    }
    __calcFiltersTaksSummary(from){
        let vencidosCount = 0;
        let semPrazoCount = 0;
        let hoje = dateToday({native:true});
        this.body.querySelectorAll('.callout').forEach((el) => {
            if(el.dataset?.termino && el.dataset.termino < hoje && parseInt(el.dataset?.progresso || 0) < 100){vencidosCount++}
            // --
            let inicioValid = el.dataset?.inicio && el.dataset.inicio != '';
            let terminoValid = el.dataset?.termino && el.dataset.termino != '';
            if(!inicioValid || !terminoValid){semPrazoCount++}
        });
        this.nav.querySelector('[data-filter="vencidos"] sup').innerHTML = vencidosCount;
        this.nav.querySelector('[data-filter="semPrazo"] sup').innerHTML = semPrazoCount;
    }
    addBoard(options){
        let board = document.createElement('div');board.setAttribute('data-type', 'kanbanBoard');
        board.classList = this.boardClasslist;
        let header = document.createElement('div');
        header.classList = 'row align-items-end mb-2';
        let header_name = document.createElement('div');
        header_name.classList = 'col';
        let title = this.__titleConfig(options?.title || 'Novo Grupo', 'boardHeader')
        header_name.appendChild(title);
        let header_controls = document.createElement('div');
        header_controls.classList = 'col-auto';
        header.appendChild(header_name);
        header.appendChild(header_controls);
        let dnd_container = document.createElement('div');
        dnd_container.classList = this.sortableClasslist;
        dnd_container.style.minHeight = '120px';
        if(!this.readOnly){
            header.style.cursor = 'move';
            new Sortable(dnd_container,this.dndTasksOptions);
            this.__boardAddControls(header_controls, dnd_container); // Adiciona controles ao board
        }
        board.appendChild(header);
        board.appendChild(dnd_container);
        this.body.appendChild(board);
        return dnd_container;
    }
    __titleConfig(text, type){
        let title = document.createElement('h6');
        title.setAttribute('data-type', type);
        title.classList = 'mb-1 text-muted';
        title.innerHTML = text;
        if(!this.readOnly){
            title.ondblclick = () => this.__changeTitle(title, type);
            if(true){
                title.setAttribute('data-long-press-delay','600');
                title.addEventListener('long-press', () => {this.__changeTitle(title, type)});
            }
        }
        return title;
    }
    __changeTitle(title, type){ // Adiciona edicao do titulo do board no duplo click, 'Enter' para salvar resultado
        let input = document.createElement('input');
        input.classList = 'form-control form-control-sm';
        input.type = 'text';
        input.value = title.innerText;
        input.onkeydown = (e) => {
            if(e.key == 'Enter'){
                if(input.value.trim() == ''){input.value = 'Titulo Obrigatorio';input.select();return false;}
                let h6 = this.__titleConfig(input.value, type);
                input.after(h6);
                input.remove();
            }
        };
        title.after(input);
        title.remove();
        input.select();
    }
    __boardAddControls(header_controls, dnd_container){
        let dropdown = document.createElement('div');dropdown.classList = 'dropdown';
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'btn btn-sm bg-body-secondary';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-caret-down"></i>';
        let dropdownMenu = document.createElement('ul');dropdownMenu.classList = 'dropdown-menu dropdown-menu-end fs-7';
        if(this.canAddTask){
            let addBtn = document.createElement('li');addBtn.classList = 'dropdown-item pointer';addBtn.innerHTML = '<i class="fas fa-plus text-success fa-fw"></i> Nova Task';
            addBtn.onclick = () => {this.addTask(dnd_container);this.__calcFiltersTaksSummary('addTaskOnclick');};
            dropdownMenu.appendChild(addBtn);
        }
        if(this.canDeleteBoard){
            let divider = document.createElement('li');divider.innerHTML = '<hr class="dropdown-divider">';
            let deleteBtn = document.createElement('li');deleteBtn.classList = 'dropdown-item dropdown-item-danger pointer';deleteBtn.innerHTML = '<i class="fas fa-trash fa-fw"></i> Lixeira';
            deleteBtn.onclick = () => {
                let board = header_controls.parentNode.parentNode;
                document.body.click(); // Aciona click do body para evitar que dropdown do bootstrap seja exibido altomaticamente no restore
                this.trash.push(board);
                board.remove();
                this.restoreButton.disabled = false; // Habilita botao para restaurar board
            };
            dropdownMenu.appendChild(divider);
            dropdownMenu.appendChild(deleteBtn);
        }
        // --------------------
        dropdown.appendChild(dropdownLink);
        dropdown.appendChild(dropdownMenu);
        header_controls.appendChild(dropdown);
    }
    restoreLastBoard(){
        if(this.trash.length > 0){
            this.body.appendChild(this.trash.pop());
            if(this.trash.length == 0){this.restoreButton.disabled = true;}
        }
    }
    addTask(dnd_container, options={}){
        let task = document.createElement('div');task.classList = this.taskClasslist;task.style.borderLeftColor = options?.cor || '#e9ecef';
        task.setAttribute('data-type','task');
        task.setAttribute('data-cor', options?.cor || '#e9ecef');
        if(options?.inicio || false){task.setAttribute('data-inicio', options.inicio)}
        if(options?.termino || false){task.setAttribute('data-termino', options.termino)}
        if(options?.responsavel || false){task.setAttribute('data-responsavel', options.responsavel)}
        if(options?.progresso || false){task.setAttribute('data-progresso', options.progresso)}
        let body = document.createElement('div');body.classList = 'body ps-0 pb-2';
        let title = this.__titleConfig(options?.titulo || 'Nova Task', 'taskTitulo');
        let description = this.__descriptionConfig(options?.descricao || 'Descrição da nova task');
        let footer = document.createElement('div');footer.classList = 'row bg-light fs-8';
        let footLeftCol = document.createElement('div');footLeftCol.classList = 'col-auto p-1';
        let taskColorInput = document.createElement('input');taskColorInput.type = 'color';taskColorInput.classList = 'form-control p-1 h-100 d-inline-block';taskColorInput.style.width = '50px';taskColorInput.value = options?.cor || '#e9ecef';
        if(!this.readOnly){
            taskColorInput.onchange = () => {
                task.setAttribute('data-cor', taskColorInput.value);
                task.style.borderLeftColor = taskColorInput.value;
            };
        }
        else{taskColorInput.disabled = true;}
        let responsavelLabel = document.createElement('div');responsavelLabel.classList = 'fw-bold text-purple d-inline-block h-100 align-middle ps-2';responsavelLabel.setAttribute('data-type','taskResponsavel');responsavelLabel.innerHTML = options?.responsavel || '';
        let footRightCol = document.createElement('div');footRightCol.classList = 'col p-1 d-flex justify-content-end';
        body.appendChild(title);
        body.appendChild(description);
        for(let tag in options.tags){ // Adiciona as tags precadastradas na task
            let objTag = this.__getTag(options.tags[tag]);
            if(objTag){this.__taskAddTag(body, objTag)}
        }
        let config = document.createElement('button');config.classList = 'btn btn-sm bg-body-tertiary text-muted fs-8';config.innerHTML = '<i class="fas fa-sliders-h"></i>';
        if(!this.readOnly){
            let tags = this.__tagsConfig(body); // Controle para adicionar tags
            config.onclick = () => {
                this.modalTaskTarget = task; // Armazena a tag a ser editada
                document.getElementById('kanbanTaskModalTitulo').value = body.querySelector('h6').innerHTML;
                document.getElementById('kanbanTaskModalDetalhe').value = body.querySelector('p').innerHTML;
                document.getElementById('kanbanTaskModalResponsavel').value = task.querySelector('[data-type="taskResponsavel"]').innerHTML;
                document.getElementById('kanbanTaskModalProgress').value = task.querySelector('[data-type="taskProgress"]').style.width.replace('%', '');
                document.getElementById('kanbanTaskModalInicio').value = task.dataset?.inicio || '';
                document.getElementById('kanbanTaskModalTermino').value = task.dataset?.termino || '';
                document.getElementById('kanbanTaskModalProgress').onchange(); // Aciona o evento change para ajustar a label do progress
                if(this.canDeleteTask){
                    document.querySelector('[data-type="modalExtra"]').onclick = () => {
                        this.modalTask.hide();
                        this.modalDeleteComponent._element.querySelector('[data-type="modalAction"]').onclick = () => {
                            this.modalTaskTarget.remove();
                            this.modalDeleteComponent.hide();
                        }
                        this.modalDeleteComponent.show();
                    };
                }
                this.modalTask.show();
            };
            footRightCol.appendChild(tags);
        }
        else{config.disabled = true;}
        footRightCol.appendChild(config);
        let progressContainer = document.createElement('div');progressContainer.classList = 'progress'; progressContainer.style.height = '3px';progressContainer.style.marginLeft = 'calc(var(--bs-gutter-x) * .5 * -1)';progressContainer.style.marginRight = 'calc(var(--bs-gutter-x) * .5 * -1)';
        let progress = document.createElement('div');progress.setAttribute('data-type','taskProgress');progress.classList = 'progress-bar bg-success bg-opacity-75'; progress.style.width = options?.progresso || '0%';
        progressContainer.appendChild(progress);
        // ---------------------
        footLeftCol.appendChild(taskColorInput);
        footLeftCol.appendChild(responsavelLabel);
        footer.appendChild(footLeftCol);
        footer.appendChild(footRightCol);
        task.appendChild(body);
        task.appendChild(footer);
        task.appendChild(progressContainer);
        dnd_container.appendChild(task);
    }
    __descriptionConfig(text){
        let desc = document.createElement('p');
        desc.classList = 'mb-2 text-muted fs-7';
        desc.innerHTML = text;
        if(!this.readOnly){desc.ondblclick = () => this.__changeDescription(desc);}
        return desc;        
    }
    __changeDescription(el){ // Implementa edicao do elemento desciption da task
        let input = document.createElement('input');
        input.classList = 'form-control form-control-sm';
        input.type = 'text';
        input.value = el.innerText;
        input.onkeydown = (e) => {
            if(e.key == 'Enter'){
                if(input.value.trim() == ''){input.value = '...';}
                let h6 = this.__descriptionConfig(input.value);
                input.after(h6);
                input.remove();
            }
        };
        el.after(input);
        el.remove();
        input.select();
    }
    __tagsConfig(taskBody){
        let dropdown = document.createElement('div');dropdown.classList = 'dropdown dropup';
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'btn btn-sm bg-body-tertiary text-muted fs-8 me-1';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-tags"></i>';
        dropdownLink.onclick = (e) => { // Carrega tags no menu do dropdown
            if(Object.keys(this.tags).length == 0){dropdownMenu.classList.remove('show');dropdownLink.classList.remove('show');return false;} // Se nao existe tag cadastrada, nao exibe menu do dropdown
            dropdownMenu.innerHTML = ''; // Limpa tags (caso carregado anteriormente)
            let currentTagsQr = taskBody.querySelectorAll('[data-tag]'); // Busca as tags atuais da task
            let currentTags = [];
            for(let i = 0; i < currentTagsQr.length; i++){currentTags.push(currentTagsQr[i].dataset.tag)} // Popula array com o nome das taks
            for(let tagId in this.tags){
                if(!currentTags.includes(this.tags[tagId].text)){ // Se tag nao estiver incluida na task, mostra no dropdown menu
                    let tag = document.createElement('li');
                    tag.classList = 'dropdown-item pointer border rounded mb-1';
                    tag.style.color = this.tags[tagId].color;
                    tag.style.backgroundColor = this.tags[tagId].bg;
                    tag.innerHTML = this.tags[tagId].text;
                    tag.onclick = () => {this.__taskAddTag(taskBody, this.tags[tagId])};
                    dropdownMenu.appendChild(tag);
                }
            }
            // Avalia se nenhuma task foi adicionada, e tambem oculta dropdown menu
            // Necessario caso exista tag cadastrada, porem ja inserida na task, ou seja nenhuma nova a exibir
            if(!dropdownMenu.hasChildNodes()){dropdownMenu.classList.remove('show');dropdownLink.classList.remove('show');return false;}
        };
        let dropdownMenu = document.createElement('ul');dropdownMenu.classList = 'dropdown-menu dropdown-menu-end px-3 fs-7 text-center';
        dropdown.appendChild(dropdownLink);
        dropdown.appendChild(dropdownMenu);
        return dropdown;
    }
    __taskAddTag(tagBody, tag){
        let lbl = document.createElement('span');
        lbl.classList = 'px-2 py-1 me-1 border rounded fs-8';
        lbl.innerHTML = tag.text;
        lbl.setAttribute('data-tag', tag.text);
        lbl.style.backgroundColor = tag.bg;
        lbl.style.color = tag.color;
        if(!this.readOnly){
            lbl.ondblclick = () => lbl.remove();
        }
        tagBody.appendChild(lbl);
    }
    __tagChangeValue(tag, prepend='', attr=null){
        let classList = tag.classList;
        let input = document.createElement('input');input.classList = 'form-control form-control-sm';input.value = tag.innerText;
        input.onkeydown = (e) => {
            if(e.key == 'Enter'){
                if(input.value.trim() == ''){input.remove()} // Se tag for vazia, remove a tag
                else{
                    let newTag = document.createElement('span');newTag.classList = classList;newTag.innerHTML = `${prepend}${input.value}`;
                    if(attr){for(let key in attr){newTag.setAttribute(key, attr[key]);}} // Seta atributos adicionais da label (se definido attr={key:value})
                    newTag.ondblclick = () => {this.__tagChangeValue(newTag,prepend,attr);};
                    input.after(newTag);
                    input.remove();
                }
            }
        };
        tag.after(input);
        tag.remove();
        input.select();
    }
    __getTag(text){ // Retorna a tag pelo text (ou null caso nao encontrado)
        for(let tag in this.tags){
            if(this.tags[tag].text == text){return this.tags[tag]}
        }
        return null;
    }
    __taskDelete(taskBody){taskBody.parentNode.remove();}
    __taskConfirmDelete(taskBody){
        let deleteBtn = this.modalDeleteComponent._element.querySelector('[data-type="modalAction"]');
        deleteBtn.onclick = () => {
            this.__taskDelete(taskBody);
            this.modalDeleteComponent.hide();
            deleteBtn.onclick = () => console.log('Kanban: Nothing to do..');
        };
        this.modalDeleteComponent.show();
    }
    __loadData(kanban_index=null){ // Monta kanban a partir do this.data
        this.currentKanban = kanban_index || 0;
        this.kanbanSelect.querySelectorAll('[data-type="kanbanLink"]').forEach((el) => el.remove());
        let divider = this.kanbanSelect.querySelector('[data-type="selectKanbanDivider"]');
        for(let kanban in this.data.kanbans){ // Percorre os kanbans, montando o select
            let kanbanLink = document.createElement('li');kanbanLink.classList = 'dropdown-item pointer';kanbanLink.setAttribute('data-type', 'kanbanLink');kanbanLink.setAttribute('data-kanban', kanban);kanbanLink.innerHTML = this.data.kanbans[kanban].id;
            if(this.currentKanban == kanban){kanbanLink.classList.add('disabled')}
            kanbanLink.onclick = () => {
                this.dataSaveCurrent(); // Salva no objeto data os kabnbans e demais elementos
                this.currentKanban = kanban; // Aponta para o novo kanban
                this.__showKanban(); // Exibe o kanban
            }
            divider.before(kanbanLink);
        }
        this.__navReorderTags(); // Monta tags
        this.__showKanban(); // Exibe boards e tasks do kanban atual
    }
    loadData(json){
        this.data = json;
        this.__loadData();
    }
    __loadTags(){
        this.tags = {...this.data.global_tags}; // Reinicia o dicionario de tags com as tags globais do objeto
        let tagsCount = Object.keys(this.tags).length;
        for(let tag in this.data.kanbans[this.currentKanban].tags){ // Adiciona as tags locais no dicionario de tags
            this.tags[tagsCount] = this.data.kanbans[this.currentKanban].tags[tag];
            tagsCount++;
        }
        this.__navReorderTags(); // Monta o navtags
    }
    __showKanban(){
        this.body.innerHTML = ''; // Limpa a exibicao atual
        this.searchInput.value = ''; // Limpa search input
        this.nav.querySelector('[data-type="navCleanFilter"]').classList.add('d-none'); // Oculta link para limpar filtros (caso exibido)
        this.kanbanSelect.querySelectorAll('[data-type="kanbanLink"].disabled').forEach((el) => el.classList.remove('disabled')); // Remove a classe disabled referente ao kanban atual
        this.kanbanSelect.querySelector(`[data-kanban="${this.currentKanban}"]`).classList.add('disabled');
        this.kanbanModalBtn.innerHTML = this.data.kanbans[this.currentKanban].id; // Altera o id do kanban no botao de edicao
        this.__loadTags(); // Refaz a lista de tags para o kanban
        for(let board in this.data.kanbans[this.currentKanban].boards){ // Adiciona os boards do kanban
            let dnd_container = this.addBoard({title: this.data.kanbans[this.currentKanban].boards[board].titulo}); // Adiciona o board
            for(let task in this.data.kanbans[this.currentKanban].boards[board].tasks){ // Adiciona as taks no board
                let task_options = {
                    titulo: this.data.kanbans[this.currentKanban].boards[board].tasks[task].titulo,
                    descricao: this.data.kanbans[this.currentKanban].boards[board].tasks[task].descricao,
                    cor: this.data.kanbans[this.currentKanban].boards[board].tasks[task].cor,
                    responsavel: this.data.kanbans[this.currentKanban].boards[board].tasks[task].responsavel,
                    inicio: this.data.kanbans[this.currentKanban].boards[board].tasks[task].inicio,
                    termino: this.data.kanbans[this.currentKanban].boards[board].tasks[task].termino,
                    progresso: this.data.kanbans[this.currentKanban].boards[board].tasks[task].progresso,
                    tags: this.data.kanbans[this.currentKanban].boards[board].tasks[task]?.tags || []
                };
                this.addTask(dnd_container, task_options);
            }            
        }
        this.__calcFiltersTaksSummary('showkanban'); // Recalcula o contador dos resumo do nav
    }
    __buildModals(){
        // Modal de confirmacao para delete task
        let modalDeleteBody = document.createElement('p');
        modalDeleteBody.innerHTML = '<h5>Excluir registro</h5><p>Confirma a exclusão do registro? Este processo <b>não pode ser desfeito</b>.</p>';
        this.modalDeleteComponent = this.__newBootstrapModal({body: modalDeleteBody,actionClass: 'danger', actionText:'Deletar'});
        // Modal para edicao das tasks
        let taskModalBody = document.createElement('div');taskModalBody.classList = 'mb-2';
        let L1Row = document.createElement('div');L1Row.classList = 'row g-1';
        let L1ColA = document.createElement('div');L1ColA.classList = 'form-floating col-md-8 mb-md-1';
        let titulo = document.createElement('input');titulo.type = 'text';titulo.classList = 'form-control';titulo.id = 'kanbanTaskModalTitulo';titulo.placeholder = ' ';
        let tituloLabel = document.createElement('label');tituloLabel.setAttribute('for', 'kanbanTaskModalTitulo');tituloLabel.innerHTML = 'Titulo';
        L1ColA.appendChild(titulo);L1ColA.appendChild(tituloLabel);
        let L1ColB = document.createElement('div');L1ColB.classList = 'form-floating col-md-4 mb-1';
        let responsavel = document.createElement('input');responsavel.type = 'text';responsavel.classList = 'form-control';responsavel.id = 'kanbanTaskModalResponsavel';responsavel.placeholder = ' ';
        let responsavelLabel = document.createElement('label');responsavelLabel.setAttribute('for', 'kanbanTaskModalResponsavel');responsavelLabel.innerHTML = 'Responsável';
        L1ColB.appendChild(responsavel);L1ColB.appendChild(responsavelLabel);
        L1Row.appendChild(L1ColA);L1Row.appendChild(L1ColB);
        let L2Row = document.createElement('div');L2Row.classList = 'row g-1';
        let L2ColA = document.createElement('div');L2ColA.classList = 'col-md-8 mb-md-1';
        let detalhe = document.createElement('textarea');detalhe.classList = 'form-control';detalhe.id = 'kanbanTaskModalDetalhe';detalhe.style.minHeight = '120px';detalhe.placeholder = 'Detalhes da task';
        L2ColA.appendChild(detalhe);
        L2Row.appendChild(L2ColA);
        let L2ColB = document.createElement('div');L2ColB.classList = 'col-md-4';
        let L2ColB_A = document.createElement('div');L2ColB_A.classList = 'form-floating mb-1';
        let inicio = document.createElement('input');inicio.type = 'date';inicio.classList = 'form-control';inicio.id = 'kanbanTaskModalInicio';
        let inicioLabel = document.createElement('label');inicioLabel.setAttribute('for', 'kanbanTaskModalInicio');inicioLabel.innerHTML = 'Inicio';
        L2ColB_A.appendChild(inicio);L2ColB_A.appendChild(inicioLabel);
        let L2ColB_B = document.createElement('div');L2ColB_B.classList = 'form-floating mb-1';
        let termino = document.createElement('input');termino.type = 'date';termino.classList = 'form-control';termino.id = 'kanbanTaskModalTermino';
        let terminoLabel = document.createElement('label');terminoLabel.setAttribute('for', 'kanbanTaskModalTermino');terminoLabel.innerHTML = 'Termino';
        L2ColB_B.appendChild(termino);L2ColB_B.appendChild(terminoLabel);
        L2ColB.appendChild(L2ColB_A);L2ColB.appendChild(L2ColB_B);
        L2Row.appendChild(L2ColB);
        let L3Row = document.createElement('div');L3Row.style.maxWidth = '250px';
        let progressLabel = document.createElement('label');progressLabel.classList = 'fs-7 mt-1';progressLabel.setAttribute('for', 'kanbanTaskModalProgress');progressLabel.innerHTML = 'Conclusão ( 0% )';
        let progress = document.createElement('input');progress.type = 'range';progress.classList = 'form-range';progress.id = 'kanbanTaskModalProgress';
        progress.min = '0';progress.max = '100';progress.value = '0';progress.step = '10';
        progress.onchange = () => {progressLabel.innerHTML = `Progresso ( ${progress.value}% )`};
        L3Row.appendChild(progressLabel);L3Row.appendChild(progress);
        taskModalBody.appendChild(L1Row);
        taskModalBody.appendChild(L2Row);
        taskModalBody.appendChild(L3Row);
        let modalTaskOptions = {body: taskModalBody,dialog_class:'modal-lg'};
        if(this.canDeleteTask){
            modalTaskOptions.btnExtra = true;
            modalTaskOptions.extraClass = 'danger';
            modalTaskOptions.extraText = 'Excluir';
        }
        this.modalTask = this.__newBootstrapModal(modalTaskOptions);
        this.modalTaskAction = this.modalTask._element.querySelector('[data-type="modalAction"]');
        this.modalTaskAction.onclick = () => {
            this.modalTaskTarget.querySelector('h6').innerHTML = titulo.value != '' ? titulo.value : 'Titulo Obrigatorio';
            this.modalTaskTarget.querySelector('p').innerHTML = detalhe.value != '' ? detalhe.value : '...';
            this.modalTaskTarget.querySelector('[data-type="taskResponsavel"]').innerHTML = responsavel.value;
            this.modalTaskTarget.querySelector('[data-type="taskProgress"]').style.width = `${progress.value}%`;
            this.modalTaskTarget.setAttribute('data-inicio', inicio.value);
            this.modalTaskTarget.setAttribute('data-termino', termino.value);
            this.modalTaskTarget.setAttribute('data-responsavel', responsavel.value);
            this.modalTaskTarget.setAttribute('data-progresso', `${progress.value}%`);
            this.modalTask.hide();
            this.__calcFiltersTaksSummary('modalTaskAction.onclick'); // Recalcula o contador dos resumo do nav
        };
        // --------------------
        let kanbanModalBody = document.createElement('div');kanbanModalBody.classList = 'mb-3';
        let kanbanId = document.createElement('input');kanbanId.type = 'text';kanbanId.classList = 'form-control';kanbanId.id = 'kanbanModalId';kanbanId.placeholder = 'ID para o kanban';
        kanbanModalBody.appendChild(kanbanId);
        let modalKanbanOptions = {body: kanbanModalBody,dialog_class:'modal-sm', btnExtra:true, extraClass: 'danger', extraText:'Excluir'};
        this.modalKanban = this.__newBootstrapModal(modalKanbanOptions);
        // --------------------
        if(this.showCleanKanbanBtn){
            let cleanKanbanTasksModal = document.createElement('p');
            cleanKanbanTasksModal.innerHTML = '<h5>Limpar tasks</h5><p>Este processo vai apagar todas as tasks para o kanban em exibição, confirma operação?</p>';
            this.modalKanbanCleanTasks = this.__newBootstrapModal({body: cleanKanbanTasksModal,actionClass: 'danger', actionText:'Limpar'});
            this.modalKanbanCleanTasks._element.querySelector('[data-type="modalAction"]').onclick = () => { // Configura o botao action do modal
                this.data.kanbans[this.currentKanban].boards.forEach((el) => {
                    el.tasks = [];
                });
                this.modalKanbanCleanTasks.hide();
                this.__showKanban();
            };
        }
        
    }
    __newBootstrapModal(options){
        let modal = document.createElement('div');modal.classList = 'modal fade';modal.tabIndex = '-1';
        if(options?.id){modal.id = options.id}
        let modalDialog = document.createElement('div');modalDialog.classList = `modal-dialog${' ' + options?.dialog_class || ''}`;
        let modalContent = document.createElement('div');modalContent.classList = 'modal-content';
        let modalHeader = document.createElement('div');modalHeader.classList = 'modal-content';
        let modalBody = document.createElement('div');modalBody.classList = 'modal-body';
        if(options?.body){modalBody.appendChild(options.body)};
        let modalFooter = document.createElement('div');modalFooter.classList = 'text-end';
        let modalBtnCancel = document.createElement('button');modalBtnCancel.classList = 'btn btn-sm btn-secondary';modalBtnCancel.setAttribute('data-bs-dismiss','modal');modalBtnCancel.innerHTML = 'Cancelar';modalBtnCancel.setAttribute('data-type', 'modalCancel');
        let modalBtnAction = document.createElement('button');modalBtnAction.setAttribute('data-type', 'modalAction');
        modalBtnAction.classList = `btn btn-sm btn-${options?.actionClass || 'primary'} ms-1`;
        modalBtnAction.innerHTML = options?.actionText || 'Gravar';
        modalBtnAction.onclick = () => console.log('Kanban: Nothing to do..');
        if(options?.btnExtra || false){
            let modalBtnExtra = document.createElement('button');modalBtnExtra.setAttribute('data-type', 'modalExtra');
            modalBtnExtra.classList = `btn btn-sm btn-${options?.extraClass || 'primary'} float-start`;
            modalBtnExtra.innerHTML = options?.extraText || 'Extra';
            modalBtnExtra.onclick = () => console.log('Kanban: Nothing to do..');
            modalFooter.appendChild(modalBtnExtra);
        }
        // ------------------
        modalFooter.appendChild(modalBtnCancel);
        modalFooter.appendChild(modalBtnAction);
        modalBody.appendChild(modalFooter);
        modalContent.appendChild(modalBody);
        modalDialog.appendChild(modalContent);
        modal.appendChild(modalDialog);
        this.container.after(modal);
        let elModal = new bootstrap.Modal(modal, {keyboard: true});
        return elModal;
    }
    tagFilter(tag){
        this.body.querySelectorAll('.callout').forEach((el) => {
            if(el.querySelectorAll(`[data-tag="${tag}"]`).length > 0){
                el.classList.remove('d-none');
            }
            else{el.classList.add('d-none')}
        });
        this.nav.querySelectorAll('[data-tag].fw-bold,[data-type="navFilter"]').forEach((el) => el.classList.remove('fw-bold', 'text-primary'));
        this.nav.querySelector(`[data-tag="${tag}"]`).classList.add('fw-bold','text-primary'); // Destaca link da tag na nav
        this.nav.querySelector('[data-type="navCleanFilter"]').classList.remove('d-none'); // Exibe o link para limpar os filtros
    }
    cleanFilters(){
        this.nav.querySelectorAll('[data-tag].fw-bold,[data-type="navFilter"]').forEach((el) => el.classList.remove('fw-bold', 'text-primary'));
        this.searchInput.value = ''; // Limpa o search input
        this.body.querySelectorAll('.callout').forEach((el) => {el.classList.remove('d-none');el.style.display = 'block';});
        this.nav.querySelector('[data-type="navCleanFilter"]').classList.add('d-none');
    }
    filter(criterio){
        let tasks = this.body.querySelectorAll('.callout:not(.d-none)');
        tasks.forEach((el) => {
            if(criterio == '' || el.innerText.toLowerCase().includes(criterio.toLowerCase())){el.style.display = 'block';}
            else{el.style.display = 'none';}
        });
    }
    // ----------------------------------------------------------------------------------------------
    dataSaveCurrent(){ // Salva o kanban atual no objeto this.data.kanbans[xx]...
        let kanban = this.data.kanbans[this.currentKanban];
        this.data.global_tags = []; // Limpa a lista de tags globais
        kanban.tags = []; // Limpa a lista de tags
        for(let tag in this.tags){ // Carrega as tags
            if(this.tags[tag].global){this.data.global_tags.push(this.tags[tag])}
            else{kanban.tags.push(this.tags[tag])}
        }
        let boards = this.body.querySelectorAll('[data-type="kanbanBoard"]');
        kanban.boards = []; // Limpa os boards antigos
        for(let i = 0; i < boards.length; i++){ // Percorre os boards
            let tasks = boards[i].querySelectorAll('[data-type="task"]'); // Busca todos as tasks no body da pagina
            let novasTasks = [];
            for(let j = 0; j < tasks.length;j++){
                let dataset = tasks[j].dataset;
                if(dataset.hasOwnProperty('type')){delete dataset['type']} // Prorpiedade type nao eh salva no objeto json
                let novasTags = [];
                let taskTags = tasks[j].querySelectorAll('[data-tag]').forEach((el) => novasTags.push(el.dataset.tag)); // Carrega as tags ajustadas para a task
                novasTasks.push({
                    titulo: tasks[j].querySelector('[data-type="taskTitulo"]').innerHTML,
                    descricao: tasks[j].querySelector('p').innerHTML,
                    tags: novasTags,
                    ...dataset
                });
            }
            kanban.boards.push({
                titulo: boards[i].querySelector('[data-type="boardHeader"]').innerHTML,
                tasks: novasTasks
            });
        }

    }
    getJson(){ // Retorna objeto json
        this.dataSaveCurrent(); // Salva kanban em exibicao
        return this.data;
    }
    exportJson(e){
        let data = JSON.stringify(this.getJson());
        let dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(data);
        let filename = 'kanban.json';
        let btn = document.createElement('a');
        btn.classList = 'd-none';
        btn.setAttribute('href', dataUri);
        btn.setAttribute('download', filename);
        btn.click();
        btn.remove();
        let originalClasslist = e.target.className;
        e.target.classList = 'btn btn-sm btn-success';
        try {dotAlert('success', 'Arquivo <b>json</b> gerado com <b>sucesso</b>')}catch(error){}
        setTimeout(function() {e.target.classList = originalClasslist;}, 800);
    }
    startFromScratch(){
        this.currentKanban = 0; // Aponta para o kanban 0 ()
        this.data = { // Inicializa a estrutura do objeto kanban
            global_tags : {},
            kanbans: [{
                id: "Sem nome",
                tags: [],
                boards: []
            }]
        };
        let defaultOpt = document.createElement('li');defaultOpt.classList = 'dropdown-item pointer disabled';defaultOpt.innerHTML = 'Sem nome';defaultOpt.setAttribute('data-type', 'kanbanLink');defaultOpt.setAttribute('data-kanban', '0');
        defaultOpt.onclick = () => {
            this.dataSaveCurrent(); // Salva no objeto data os kabnbans e demais elementos
            this.currentKanban = 0; // Aponta para o kanban default
            this.__showKanban(); // Exibe o kanban
        }
        this.kanbanSelect.querySelector('[data-type="selectKanbanDivider"]').before(defaultOpt);
    }
}