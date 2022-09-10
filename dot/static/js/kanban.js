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
        this.tags = {
            1:{text:'Teste', color: '#DC3545', bg: '#F8F9FA'},
            2:{text:'Uii', color: '#CCC', bg: '#F57900'},
        }; // armazena as tags cadastradas
        this.modalDeleteTask = null; // aponta para instancia (bootstrap modal) do modal para deletar task
        // Configuracao
        // this.boards = options?.data || []; // Json com dados dos boards kanban
        this.container = options?.container || document.body; // parentNode do kanban, create(), caso nao informado append no body
        this.sortableClasslist = options?.sortableClasslist || 'pb-5'; // classlist para o div drag and drop
        this.dndBoardsOptions = options?.dndBoardsOptions || {group:'boards',animation:100, dragClass: 'dragging'}; // options da instancia Sortable JS dos boards
        this.dndTasksOptions = options?.dndTasksOptions || {group:'tasks', dragClass: 'dragging'}; // options da instancia Sortable JS das tasks
        this.readOnly = options?.readOnly != undefined ? options.readOnly : false; // Boolean, se setado para true desativa todas as opcoes de edicao do kanban
        this.canAddBoard = options?.canAddBoard != undefined ? options.canAddBoard : true; // Boolean, exibe/oculta controle para novo board
        this.canAddTask = options?.canAddTask != undefined ? options.canAddTask : true; // Boolean, exibe/oculta controle para nova task no grupo
        this.canDeleteBoard = options?.canDeleteBoard != undefined ? options.canDeleteBoard : true; // Boolean, exibe/oculta controle para deletar board
        this.canDeleteTask = options?.canDeleteTask != undefined ? options.canDeleteTask : false; // Boolean, exibe/oculta controle para deletar task
        // Estilizacao
        this.kanbanClasslist = options?.kanbanClasslist || 'row'; // classlist para o container principal
        this.headerClasslist = options?.headerClasslist || 'col-12 bg-white p-2'; // classlist para o header container
        this.navContainerClasslist = options?.navContainerClasslist || 'col-auto pt-3 bg-light rounded ps-2 pe-5'; // classlist para o nav container
        this.navClasslist = options?.navClasslist || 'text-muted'; // classlist para o nav (ul)
        this.bodyContainerClasslist = options?.bodyContainerClasslist || 'col p-3'; // classlist para o board container
        this.bodyClasslist = options?.bodyClasslist || 'row'; // classlist para o board
        this.boardClasslist = options?.boardClasslist || 'col-2'; // classlist para o board
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
        let nav_container = document.createElement('div'); // Col, container para o menu de navegacao das tasks
        nav_container.classList = this.navContainerClasslist;
        nav_container.innerHTML = 'NAV'; // REMOVER AQUI
        let bodyCol = document.createElement('div'); // Col, container para o this.body
        bodyCol.classList = this.bodyContainerClasslist;
        this.body = document.createElement('div'); // Row que agrupa os boards 
        this.body.classList = this.bodyClasslist;
        new Sortable(this.body,this.dndBoardsOptions);
        // --------------------------------
        bodyCol.appendChild(this.body);
        this.kanban.appendChild(this.header);
        this.kanban.appendChild(nav_container);
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
    buildNav(){}
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
        let description = this.__descriptionConfig('Descrição da nova task');
        let footer = document.createElement('div');footer.classList = 'row bg-light fs-8';
        let footLeftCol = document.createElement('div');footLeftCol.classList = 'col p-1';
        let changeColorBtn = document.createElement('button');changeColorBtn.classList = 'btn btn-sm btn-light text-muted fs-8';changeColorBtn.innerHTML = '<i class="fas fa-circle me-1"></i> <span data-type="task-color">#6C757D</span>';
        changeColorBtn.onclick = () => {
            let inputColor = document.createElement('input');
            inputColor.type = 'color';
            inputColor.style.display = 'none';
            inputColor.onchange = () => {
                changeColorBtn.classList.remove('text-muted');
                changeColorBtn.style.color = inputColor.value;
                changeColorBtn.innerHTML = `<i class="fas fa-circle me-1"></i> <span data-type="task-color">${inputColor.value}</span>`;
                task.style.borderLeftColor = inputColor.value;
                inputColor.remove();
            };
            inputColor.click();
        };
        let footRightCol = document.createElement('div');footRightCol.classList = 'col-auto p-1 btn-group';
        let tags = this.__tagsConfig(body); // Controle para adicionar tags
        let config = this.__taskConfig(body, {'responsavel':'rafitas'}); // Controle de campos adicionais da task
        // ---------------------
        body.appendChild(title);
        body.appendChild(description);
        footLeftCol.appendChild(changeColorBtn);
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
    __tagsConfig(){
        let dropdown = document.createElement('div');dropdown.classList = 'dropdown dropup';
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'btn btn-sm btn-light text-muted fs-8';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-tags"></i>';
        let dropdownMenu = document.createElement('ul');dropdownMenu.classList = 'dropdown-menu dropdown-menu-end px-3 fs-7 text-center';
        for(let tagId in this.tags){
            let tag = document.createElement('li');tag.classList = 'dropdown-item pointer border rounded mb-1';tag.style.color = this.tags[tagId].color;tag.style.backgroundColor = this.tags[tagId].bg;tag.innerHTML = this.tags[tagId].text;
            dropdownMenu.appendChild(tag);
        }
        dropdown.appendChild(dropdownLink);
        dropdown.appendChild(dropdownMenu);
        return dropdown;
    }
    __taskConfig(taskBody, options){
        let dropdown = document.createElement('div');dropdown.classList = 'dropdown dropup';
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'btn btn-sm btn-light text-muted fs-8';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-sliders-h"></i>';
        let dropdownMenu = document.createElement('ul');dropdownMenu.classList = 'dropdown-menu dropdown-menu-end fs-7 text-center';
        let btnGroup = document.createElement('div');btnGroup.classList = 'btn-group';
        let userBtn = document.createElement('button');
        userBtn.innerHTML = '<i class="fas fa-user"></i>';
        userBtn.classList = 'btn btn-sm btn-outline-success';
        userBtn.onclick = () => this.__customTagToogle(taskBody,'responsavel', 'Nome');
        let prazoBtn = document.createElement('button');
        prazoBtn.innerHTML = '<i class="fas fa-calendar"></i>';
        prazoBtn.classList = 'btn btn-sm btn-outline-primary';
        prazoBtn.onclick = () => this.__customTagToogle(taskBody,'prazo', today(5));
        btnGroup.appendChild(userBtn);
        btnGroup.appendChild(prazoBtn);
        if(this.canDeleteTask){
            let deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
            deleteBtn.classList = 'btn btn-sm btn-outline-danger';
            deleteBtn.onclick = () => this.__taskDelete(taskBody);
            btnGroup.appendChild(deleteBtn);
        }
        dropdownMenu.appendChild(btnGroup);
        dropdown.appendChild(dropdownLink);
        dropdown.appendChild(dropdownMenu);
        return dropdown;
    }
    __taskAddLabel(tagBody, label, value){
        let lbl = document.createElement('span');
        lbl.classList = 'px-2 py-1 me-1 border rounded fs-8';
        if(label == 'responsavel'){
            lbl.classList.add('bg-success', 'bg-opacity-25', 'text-success');
            lbl.setAttribute('data-task', 'responsavel');
            lbl.innerHTML = `<i class="fas fa-user me-2"></i>${value}`;
            lbl.ondblclick = () => {this.__tagChangeValue(lbl,'<i class="fas fa-user me-2"></i>',{'data-task':'responsavel'});};
        }
        else if(label == 'prazo'){
            lbl.classList.add('bg-primary', 'bg-opacity-25', 'text-primary');
            lbl.setAttribute('data-task', 'prazo');
            lbl.innerHTML = `<i class="fas fa-calendar me-2"></i>${value}`;
            lbl.ondblclick = () => {this.__tagChangeValue(lbl,'<i class="fas fa-calendar me-2"></i>',{'data-task':'prazo'});};
        }
        else{
            lbl.classList.add('bg-danger', 'bg-opacity-25', 'text-danger');
            lbl.innerHTML = `${value}`;
        }
        tagBody.appendChild(lbl);
    }
    __customTagToogle(taskBody, data_task, defaultValue){ // Adiciona / remove custom tag (deve informa data-task)
        let resp = taskBody.querySelector(`[data-task="${data_task}"]`);
        if(resp){resp.remove();return false;} // Se ja existe tag, remove e retorna falso
        else{this.__taskAddLabel(taskBody, data_task, defaultValue);return true;}
    };
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
    __taskDelete(taskBody){
        let deleteBtn = document.getElementById('kanbanModalDeleteTaskBtnDelete');
        deleteBtn.onclick = () => {
            this.__taskConfirmDelete(taskBody);
            this.modalDeleteTask.hide();
            deleteBtn.onclick = () => console.log('Kanban: Nothing to do..');
        };
        this.modalDeleteTask.show();
    }
    __taskConfirmDelete(taskBody){
        taskBody.parentNode.remove();
    }
    __buildModals(){
        let modalDeleteTask = document.createElement('div');modalDeleteTask.id = 'kanbanModalDeleteTask';modalDeleteTask.classList = 'modal fade';modalDeleteTask.tabIndex = '-1';
        let modalDialog = document.createElement('div');modalDialog.classList = 'modal-dialog';
        let modalContent = document.createElement('div');modalContent.classList = 'modal-content';
        let modalHeader = document.createElement('div');modalHeader.classList = 'modal-content';
        let modalBody = document.createElement('div');modalBody.classList = 'modal-body';
        modalBody.innerHTML = '<p>Confirma a exlusão da Task? Este processo <b>não pode ser desfeito</b>.</p>';
        let modalFooter = document.createElement('div');modalFooter.classList = 'text-end';
        let btnCancel = document.createElement('button');btnCancel.classList = 'btn btn-sm btn-secondary';btnCancel.setAttribute('data-bs-dismiss','modal');btnCancel.innerHTML = 'Cancelar';
        let btnDelete = document.createElement('button');btnDelete.id = 'kanbanModalDeleteTaskBtnDelete';btnDelete.classList = 'btn btn-sm btn-danger ms-1';btnDelete.innerHTML = 'Deletar';btnDelete.onclick = () => console.log('Kanban: Nothing to do..');
        // ------------------
        modalFooter.appendChild(btnCancel);
        modalFooter.appendChild(btnDelete);
        modalBody.appendChild(modalFooter);
        modalContent.appendChild(modalBody);
        modalDialog.appendChild(modalContent);
        modalDeleteTask.appendChild(modalDialog);
        document.body.appendChild(modalDeleteTask);
        this.modalDeleteTask = new bootstrap.Modal('#kanbanModalDeleteTask', {keyboard: true})
    }
}