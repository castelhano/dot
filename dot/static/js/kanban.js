/* TODO
* Implementar modal para alterar task
* Filtrar tags ao clicar na tag
* Adicionar progress a task (e ao grupo?)
* Ajusta prazo para inicio e termino
* Implementar metodo filter
* Exportar json com dados
* Implementar metodo save
* Implementar metodo no app gestao (empresa, kanban, ..., file !!verificar como fazer)
*/
class Kanban{
    constructor(options){
        // Variaveis internas
        this.kanban = null; // container pai, contem todos os boards
        this.header = null; // container dos headers (id, pesquisa, etc)
        this.controls = null; // ul com controles do kanban
        this.body = null; // container do corpo do kanban (boards)
        this.nav = null; // nav para filtro e navegacao das tasks
        this.restoreButton = null; // aponta para botao de restorBoard
        this.trash = []; // armazena bords deletados
        this.tags = {}; // armazena as tags cadastradas
        this.modalTask = null; // aponta para modal com dados detalhados da task
        this.modalTaskAction = null; // aponta para o botao gravar do modal de edicao da task
        this.modalTaskTarget = null; // aponta para a task que esta sendo editada
        this.modalDeleteTask = null; // aponta para instancia (bootstrap modal) do modal para deletar task
        // Configuracao
        // this.data = options?.data || []; // Json com dados dos boards kanban
        this.container = options?.container || document.body; // parentNode do kanban, create(), caso nao informado append no body
        this.sortableClasslist = options?.sortableClasslist || 'pb-5'; // classlist para o div drag and drop
        this.dndBoardsOptions = options?.dndBoardsOptions || {group:'boards',animation:100, dragClass: 'dragging'}; // options da instancia Sortable JS dos boards
        this.dndTasksOptions = options?.dndTasksOptions || {group:'tasks', dragClass: 'dragging'}; // options da instancia Sortable JS das tasks
        this.readOnly = options?.readOnly != undefined ? options.readOnly : false; // Boolean, se setado para true desativa todas as opcoes de edicao do kanban
        this.canAddBoard = options?.canAddBoard != undefined ? options.canAddBoard : true; // Boolean, exibe/oculta controle para novo board
        this.canAddTask = options?.canAddTask != undefined ? options.canAddTask : true; // Boolean, exibe/oculta controle para nova task no grupo
        this.canAddTag = options?.canAddTag != undefined ? options.canAddTag : true; // Boolean, exibe/oculta controle para nova tag
        this.canDeleteBoard = options?.canDeleteBoard != undefined ? options.canDeleteBoard : true; // Boolean, exibe/oculta controle para deletar board
        this.canDeleteTask = options?.canDeleteTask != undefined ? options.canDeleteTask : false; // Boolean, exibe/oculta controle para deletar task
        this.canDeleteTag = options?.canDeleteTag != undefined ? options.canDeleteTag : true; // Boolean, exibe/oculta controle para deletar tag
        // Estilizacao
        this.kanbanClasslist = options?.kanbanClasslist || 'row'; // classlist para o container principal
        this.headerClasslist = options?.headerClasslist || 'col-12 bg-white p-2'; // classlist para o header container
        this.navContainerClasslist = options?.navContainerClasslist || 'col-auto bg-light text-muted rounded pt-3 ps-2 fs-7 position-relative'; // classlist para o nav container
        this.navClasslist = options?.navClasslist || 'text-muted'; // classlist para o nav (ul)
        this.bodyContainerClasslist = options?.bodyContainerClasslist || 'col p-3'; // classlist para o board container
        this.bodyClasslist = options?.bodyClasslist || 'row'; // classlist para o board
        this.boardClasslist = options?.boardClasslist || 'col-3'; // classlist para o board
        this.taskClasslist = options?.taskClasslist || ''; // classlist base para as tasks

        this.create();
        this.buildControls();
        this.buildNav();
        this.__buildModals();
        // this.addBoard();
        // this.addBoard({title:'Mais uma'});
    }
    create(){
        this.kanban = document.createElement('div'); // Row que engloba todo o kanban
        this.kanban.classList = this.kanbanClasslist;
        this.header = document.createElement('div'); // Col, container para os headers
        this.header.classList = this.headerClasslist;
        this.nav = document.createElement('div'); // Col, container para o menu de navegacao das tasks
        this.nav.classList = this.navContainerClasslist;
        let bodyCol = document.createElement('div'); // Col, container para o this.body
        bodyCol.classList = this.bodyContainerClasslist;
        this.body = document.createElement('div'); // Row que agrupa os boards 
        this.body.classList = this.bodyClasslist;
        new Sortable(this.body,this.dndBoardsOptions);
        // --------------------------------
        bodyCol.appendChild(this.body);
        this.kanban.appendChild(this.header);
        this.kanban.appendChild(this.nav);
        this.kanban.appendChild(bodyCol);
        this.container.appendChild(this.kanban);
    }
    buildControls(){
        let row = document.createElement('div');row.classList = 'row g-1';
        let colStart = document.createElement('div');colStart.classList = 'col-auto';
        let colCenter = document.createElement('div');colCenter.classList = 'col';
        let colEnd = document.createElement('div');colEnd.classList = 'col-auto';
        let groupBtn = document.createElement('div');groupBtn.classList = 'btn-group';
        if(this.canAddBoard){
            let addBoard = document.createElement('button');
            addBoard.classList = 'btn btn-sm btn-success'
            addBoard.innerHTML = '<i class="fas fa-plus me-2"></i> Board'
            addBoard.onclick = () => this.addBoard();
            groupBtn.appendChild(addBoard);
        }
        if(this.canDeleteBoard){
            this.restoreButton = document.createElement('button');
            this.restoreButton.classList = 'btn btn-sm btn-outline-secondary';
            this.restoreButton.innerHTML = '<i class="fas fa-history"></i>';
            this.restoreButton.disabled = true;
            this.restoreButton.onclick = () => this.restoreLastBoard();
            groupBtn.appendChild(this.restoreButton);
        }
        colStart.appendChild(groupBtn);
        let searchInput = document.createElement('input');searchInput.classList = 'form-control form-control-sm';
        searchInput.placeholder = 'Pesquisa..';
        colCenter.appendChild(searchInput);
        row.appendChild(colStart);
        row.appendChild(colCenter);
        row.appendChild(colEnd);
        this.header.appendChild(row);

    }
    buildNav(){
        let cleanFilter = document.createElement('span');
        cleanFilter.setAttribute('data-type', 'navCleanFilter');
        cleanFilter.classList = 'pointer text-primary position-absolute fs-8';
        cleanFilter.style.top = '3px';
        cleanFilter.style.right = '10px';
        cleanFilter.innerHTML = `Limpar`;
        this.nav.appendChild(cleanFilter);
        let menu = document.createElement('ul');menu.classList = 'list-unstyled';menu.style.minWidth = '204px';
        this.__navReorderTags(); // Insere as tags no nav de e reordena pelo nome
        if(this.canAddTag){
            let addTag = document.createElement('li');
            addTag.setAttribute('data-type', 'navNewTag');
            addTag.classList = 'pointer mt-2';
            addTag.innerHTML = `<i class="fas fa-plus fa-fw"></i>Nova tag`;
            addTag.onclick = () => {this.__navTagForm()};
            menu.appendChild(addTag);
        }
        if(this.canDeleteTag){
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
        this.nav.appendChild(menu);
    }
    __navTagForm(tag=null){ // Monta form para adicionar ou editar tag
        this.nav.querySelectorAll('[data-type="kanbanNavTagFormControl"], [data-type="kanbanNavTagFormHelp"]').forEach((el) => el.remove()); // Apaga form 'antigo' caso tentativa de gerar form duplicado
        let inputGroup = document.createElement('div');inputGroup.classList = 'input-group mt-1';inputGroup.setAttribute('data-type', 'kanbanNavTagFormControl');
        let bgColorBtn = document.createElement('input');bgColorBtn.type = 'color';bgColorBtn.classList = 'form-control form-control-sm';bgColorBtn.style.maxWidth = '50px';bgColorBtn.title = 'Cor do fundo';
        let colorBtn = document.createElement('input');colorBtn.type = 'color';colorBtn.classList = 'form-control form-control-sm';colorBtn.style.maxWidth = '50px';colorBtn.title = 'Cor do texto';
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
            let tagLabel = document.createElement('i');tagLabel.classList = `fas fa-${this.tags[i].global == 'true' ? 'tags' : 'tag'} fa-fw pointer`; tagLabel.style.color = orderedTags[i].bg;
            let tagName = document.createElement('span');tagName.classList = 'user-select-none ms-1 pointer';tagName.innerHTML = orderedTags[i].text;
            tagLabel.ondblclick = () => {
                this.__navTagForm(this.tags[i]);
            }
            tagName.onclick = () => {console.log('FILTRANDO');}
            elTag.appendChild(tagLabel);
            elTag.appendChild(tagName);
            newTagBtn.before(elTag);
        }
    }
    addBoard(options){
        let board = document.createElement('div');
        board.classList = this.boardClasslist;
        let header = document.createElement('div');
        header.classList = 'row align-items-end mb-2';
        header.style.cursor = 'move';
        let header_name = document.createElement('div');
        header_name.classList = 'col';
        let title = this.__titleConfig(options?.title || 'Novo Grupo')
        header_name.appendChild(title);
        let header_controls = document.createElement('div');
        header_controls.classList = 'col-auto';
        header.appendChild(header_name);
        header.appendChild(header_controls);
        let dnd_container = document.createElement('div');
        dnd_container.classList = this.sortableClasslist;
        dnd_container.style.minHeight = '120px';
        new Sortable(dnd_container,this.dndTasksOptions);
        this.__boardAddControls(header_controls, dnd_container); // Adiciona controles ao board
        board.appendChild(header);
        board.appendChild(dnd_container);
        this.body.appendChild(board);
    }
    __titleConfig(text){
        let title = document.createElement('h6');
        title.classList = 'mb-1 text-muted';
        title.innerHTML = text;
        title.ondblclick = () => this.__changeTitle(title);
        return title;
    }
    __changeTitle(title){ // Adiciona edicao do titulo do board no duplo click, 'Enter' para salvar resultado
        let input = document.createElement('input');
        input.classList = 'form-control form-control-sm';
        input.type = 'text';
        input.value = title.innerText;
        input.onkeydown = (e) => {
            if(e.key == 'Enter'){
                if(input.value.trim() == ''){input.value = 'Titulo Obrigatorio';input.select();return false;}
                let h6 = this.__titleConfig(input.value);
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
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'btn btn-sm btn-light';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-caret-down"></i>';
        let dropdownMenu = document.createElement('ul');dropdownMenu.classList = 'dropdown-menu dropdown-menu-end fs-7';
        if(this.canAddTask){
            let addBtn = document.createElement('li');addBtn.classList = 'dropdown-item pointer';addBtn.innerHTML = '<i class="fas fa-plus text-success fa-fw"></i> Nova Task';
            addBtn.onclick = () => this.addTask(dnd_container);
            dropdownMenu.appendChild(addBtn);
        }
        if(this.canDeleteBoard){
            let divider = document.createElement('li');divider.innerHTML = '<hr class="dropdown-divider">';
            let deleteBtn = document.createElement('li');deleteBtn.classList = 'dropdown-item dropdown-item-danger pointer';deleteBtn.innerHTML = '<i class="fas fa-trash fa-fw"></i> Excluir Board';
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
    addTask(dnd_container){
        let task = document.createElement('div');task.classList = 'callout mb-2 container-fluid';
        let body = document.createElement('div');body.classList = 'body ps-0';
        let title = this.__titleConfig('Nova Task');
        title.setAttribute('data-type', 'taskTitulo');
        let description = this.__descriptionConfig('Descrição da nova task');
        let footer = document.createElement('div');footer.classList = 'row bg-light fs-8';
        let footLeftCol = document.createElement('div');footLeftCol.classList = 'col-auto p-1';
        let taskColorInput = document.createElement('input');taskColorInput.type = 'color';taskColorInput.classList = 'form-control p-1 h-100';taskColorInput.style.width = '50px';taskColorInput.value = '#e9ecef';
        taskColorInput.onchange = () => {task.style.borderLeftColor = taskColorInput.value;};
        let footRightCol = document.createElement('div');footRightCol.classList = 'col p-1 d-flex justify-content-end';
        let tags = this.__tagsConfig(body); // Controle para adicionar tags
        let config = document.createElement('button');config.classList = 'btn btn-sm btn-light text-muted fs-8';config.innerHTML = '<i class="fas fa-sliders-h"></i>';
        config.onclick = () => {
            this.modalTaskTarget = task; // Armazena a tag a ser editada
            document.getElementById('kanbanTaskModalTitulo').value = body.querySelector('h6').innerHTML;
            document.getElementById('kanbanTaskModalDetalhe').value = body.querySelector('p').innerHTML;
            this.modalTask.show();
        };
        // ---------------------
        body.appendChild(title);
        body.appendChild(description);
        footLeftCol.appendChild(taskColorInput);
        footRightCol.appendChild(tags);
        footRightCol.appendChild(config);
        footer.appendChild(footLeftCol);
        footer.appendChild(footRightCol);
        task.appendChild(body);
        task.appendChild(footer);
        dnd_container.appendChild(task);
    }
    __descriptionConfig(text){
        let desc = document.createElement('p');
        desc.classList = 'mb-1 text-muted fs-7';
        desc.innerHTML = text;
        desc.ondblclick = () => this.__changeDescription(desc);
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
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'btn btn-sm btn-light text-muted fs-8';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-tags"></i>';
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
                    tag.onclick = () => {this.__taskAddLabel(taskBody, this.tags[tagId].text,this.tags[tagId].bg, this.tags[tagId].color)};
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
    __taskAddLabel(tagBody, value, bg, color){
        let lbl = document.createElement('span');
        lbl.classList = 'px-2 py-1 me-1 border rounded fs-8';
        lbl.innerHTML = value;
        lbl.setAttribute('data-tag', value);
        lbl.style.backgroundColor = bg;
        lbl.style.color = color;
        lbl.ondblclick = () => lbl.remove();
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
    __tagDelete(){}
    __taskDelete(taskBody){taskBody.parentNode.remove();}
    __taskConfirmDelete(taskBody){
        let deleteBtn = this.modalDeleteTask._element.querySelector('[data-type="modalAction"]');
        deleteBtn.onclick = () => {
            this.__taskDelete(taskBody);
            this.modalDeleteTask.hide();
            deleteBtn.onclick = () => console.log('Kanban: Nothing to do..');
        };
        this.modalDeleteTask.show();
    }
    __buildModals(){
        // Modal de confirmacao para delete task
        let modalDeleteBody = document.createElement('p');
        modalDeleteBody.innerHTML = '<h5>Excluir task</h5><p>Confirma a exclusão da task? Este processo <b>não pode ser desfeito</b>.</p>';
        this.modalDeleteTask = this.__newBootstrapModal({body: modalDeleteBody,actionClass: 'danger', actionText:'Deletar'});
        // Modal para edicao das tasks
        let taskModalBody = document.createElement('div');taskModalBody.classList = 'mb-2';
        let L1Row = document.createElement('div');L1Row.classList = 'row g-1';
        let L1ColA = document.createElement('div');L1ColA.classList = 'form-floating col-8 mb-1';
        let titulo = document.createElement('input');titulo.type = 'text';titulo.classList = 'form-control';titulo.id = 'kanbanTaskModalTitulo';titulo.placeholder = ' ';
        let tituloLabel = document.createElement('label');tituloLabel.setAttribute('for', 'kanbanTaskModalTitulo');tituloLabel.innerHTML = 'Titulo';
        L1ColA.appendChild(titulo);L1ColA.appendChild(tituloLabel);
        let L1ColB = document.createElement('div');L1ColB.classList = 'form-floating col-4 mb-1';
        let responsavel = document.createElement('input');responsavel.type = 'text';responsavel.classList = 'form-control';responsavel.id = 'kanbanTaskModalResponsavel';responsavel.placeholder = ' ';
        let responsavelLabel = document.createElement('label');responsavelLabel.setAttribute('for', 'kanbanTaskModalResponsavel');responsavelLabel.innerHTML = 'Responsável';
        L1ColB.appendChild(responsavel);L1ColB.appendChild(responsavelLabel);
        L1Row.appendChild(L1ColA);L1Row.appendChild(L1ColB);
        let L2Row = document.createElement('div');L2Row.classList = 'row g-1';
        let L2ColA = document.createElement('div');L2ColA.classList = 'col-8 mb-1';
        let detalhe = document.createElement('textarea');detalhe.classList = 'form-control';detalhe.id = 'kanbanTaskModalDetalhe';detalhe.style.minHeight = '120px';detalhe.placeholder = 'Detalhes da task';
        L2ColA.appendChild(detalhe);
        L2Row.appendChild(L2ColA);
        let L2ColB = document.createElement('div');L2ColB.classList = 'col-4';
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
        let conclusaoLabel = document.createElement('label');conclusaoLabel.classList = 'fs-7 mt-1';conclusaoLabel.setAttribute('for', 'kanbanTaskModalConclusao');conclusaoLabel.innerHTML = 'Conclusão ( 0% )';
        let conclusao = document.createElement('input');conclusao.type = 'range';conclusao.classList = 'form-range';conclusao.id = 'kanbanTaskModalConclusao';
        conclusao.min = '0';conclusao.max = '100';conclusao.value = '0';conclusao.step = '10';
        conclusao.onchange = () => {conclusaoLabel.innerHTML = `Conclusão ( ${conclusao.value}% )`};
        L3Row.appendChild(conclusaoLabel);L3Row.appendChild(conclusao);
        taskModalBody.appendChild(L1Row);
        taskModalBody.appendChild(L2Row);
        taskModalBody.appendChild(L3Row);
        this.modalTask = this.__newBootstrapModal({body: taskModalBody, dialog_class:'modal-lg'});
        this.modalTaskAction = this.modalTask._element.querySelector('[data-type="modalAction"]');
        this.modalTaskAction.onclick = () => {
            this.modalTaskTarget.querySelector('h6').innerHTML = titulo.value;
            this.modalTaskTarget.querySelector('p').innerHTML = detalhe.value;
            // if(responsavel.value != ''){FOOOOOOOO}
            this.modalTask.hide();
        };
        // --------------------
        
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
        let modalBtnCancel = document.createElement('button');modalBtnCancel.classList = 'btn btn-sm btn-secondary';modalBtnCancel.setAttribute('data-bs-dismiss','modal');modalBtnCancel.innerHTML = 'Cancelar';
        let modalBtnAction = document.createElement('button');modalBtnAction.setAttribute('data-type', 'modalAction');
        modalBtnAction.classList = `btn btn-sm btn-${options?.actionClass || 'primary'} ms-1`;
        modalBtnAction.innerHTML = options?.actionText || 'Gravar';
        modalBtnAction.onclick = () => console.log('Kanban: Nothing to do..');
        // ------------------
        modalFooter.appendChild(modalBtnCancel);
        modalFooter.appendChild(modalBtnAction);
        modalBody.appendChild(modalFooter);
        modalContent.appendChild(modalBody);
        modalDialog.appendChild(modalContent);
        modal.appendChild(modalDialog);
        document.body.appendChild(modal);
        let elModal = new bootstrap.Modal(modal, {keyboard: true});
        return elModal;
    }
}