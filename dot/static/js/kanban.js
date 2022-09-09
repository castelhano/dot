class Kanban{
    constructor(options){
        // Variaveis internas
        this.kanban = null; // container pai, contem todos os boards
        this.header = null; // container dos headers (id, pesquisa, etc)
        this.controls = null; // ul com controles do kanban
        this.body = null; // container do corpo do kanban (boards)
        this.nav = null; // nav para filtro e navegacao das tasks
        // Configuracao
        // this.boards = options?.data || []; // Json com dados dos boards kanban
        this.container = options?.container || document.body; // parentNode do kanban, create(), caso nao informado append no body
        this.sortableClasslist = options?.sortableClasslist || ''; // classlist para o div drag and drop
        this.dndStatusOptions = options?.dndStatusOptions || {group:'boards'}; // options da instancia Sortable JS dos boards
        this.dndTasksOptions = options?.dndTasksOptions || {group:'tasks'}; // options da instancia Sortable JS das tasks
        this.readOnly = options?.readOnly != undefined ? options.readOnly : false; // Boolean, se setado para true desativa todas as opcoes de edicao do kanban
        this.canAddStatus = options?.canAddStatus != undefined ? options.canAddStatus : true; // Boolean, exibe/oculta controle para novo status (grupo de tasks) 
        this.canAddTask = options?.canAddTask != undefined ? options.canAddTask : true; // Boolean, exibe/oculta controle para nova task no grupo
        // Estilizacao
        this.kanbanClasslist = options?.kanbanClasslist || 'row bg-light'; // classlist para o container principal
        this.headerClasslist = options?.headerClasslist || 'col-12 bg-white p-2'; // classlist para o header container
        this.navContainerClasslist = options?.navContainerClasslist || 'col-auto pt-3 ps-2 pe-5'; // classlist para o nav container
        this.navClasslist = options?.navClasslist || 'text-muted'; // classlist para o nav (ul)
        this.bodyContainerClasslist = options?.bodyContainerClasslist || 'col p-3'; // classlist para o board container
        this.bodyClasslist = options?.bodyClasslist || 'row'; // classlist para o board
        this.boardClasslist = options?.boardClasslist || 'col-2'; // classlist para o board
        this.taskClasslist = options?.taskClasslist || ''; // classlist base para as tasks

        this.create();
        this.buildNav();
        this.addBoard({title: 'Meu foo'});
    }
    create(){
        this.kanban = document.createElement('div'); // Row que engloba todo o kanban
        this.kanban.classList = this.kanbanClasslist;
        this.header = document.createElement('div'); // Col, container para os headers
        this.header.classList = this.headerClasslist;
        this.header.innerHTML = 'HEADER'; // REMOVER AQUI
        let nav_container = document.createElement('div'); // Col, container para o menu de navegacao das tasks
        nav_container.classList = this.navContainerClasslist;
        nav_container.innerHTML = 'NAV'; // REMOVER AQUI
        let bodyCol = document.createElement('div'); // Col, container para o this.body
        bodyCol.classList = this.bodyContainerClasslist;
        this.body = document.createElement('div'); // Row que agrupa os boards 
        this.body.classList = this.bodyClasslist;
        // --------------------------------
        bodyCol.appendChild(this.body);
        this.kanban.appendChild(this.header);
        this.kanban.appendChild(nav_container);
        this.kanban.appendChild(bodyCol);
        this.container.appendChild(this.kanban);
    }
    buildControls(){

    }
    buildNav(){}
    addBoard(options){
        let board = document.createElement('div');
        board.classList = this.boardClasslist;
        let header = document.createElement('div');
        header.classList = 'row align-items-end';
        let header_name = document.createElement('div');
        header_name.classList = 'col';
        header_name.innerHTML = `<h6 class="mb-1 text-muted">${options?.title || 'Novo grupo'}</h6>`;
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
    __boardAddControls(header_controls, dnd_container){
        let dropdown = document.createElement('div');dropdown.classList = 'dropdown';
        let dropdownLink = document.createElement('a');dropdownLink.classList = 'link-secondary pointer px-2';dropdownLink.setAttribute('data-bs-toggle','dropdown');dropdownLink.innerHTML = '<i class="fas fa-caret-down"></i>';
        let dropdownMenu = document.createElement('ul');dropdownMenu.classList = 'dropdown-menu dropdown-menu-end fs-7';
        if(this.canAddTask){
            let addBtn = document.createElement('li');addBtn.classList = 'dropdown-item pointer';addBtn.innerHTML = '<i class="fas fa-plus fa-fw"></i> Nova Task';
            addBtn.onclick = () => this.addTask(dnd_container);
            dropdownMenu.appendChild(addBtn);
        }
        // --------------------
        dropdown.appendChild(dropdownLink);
        dropdown.appendChild(dropdownMenu);
        header_controls.appendChild(dropdown);
    }
    addTask(dnd_container){
        let task = document.createElement('div');task.classList = 'callout mb-2';
        let body = document.createElement('div');body.classList = 'body';
        let title = document.createElement('h6');title.classList = 'text-muted'; title.innerHTML = 'Nova Task';
        let description = document.createElement('p');description.innerHTML = 'Descrição da nova task';
        let footer = document.createElement('div');footer.classList = 'footer p-1 fs-8';
        let footRow = document.createElement('div');footRow.classList = 'row';
        let footLeftCol = document.createElement('div');footLeftCol.classList = 'col';
        let changeColorBtn = document.createElement('button');changeColorBtn.classList = 'btn btn-sm btn-light text-muted fs-8';changeColorBtn.innerHTML = '<i class="fas fa-circle me-1"></i> #F1152F5';
        let footRightCol = document.createElement('div');footRightCol.classList = 'col-auto';

            // <div class="row">
            //   <div class="col"><button class="btn btn-sm btn-light text-success fs-8"></button></div>
            //   <div class="col-auto pt-1"><span class="text-muted pe-2"><span class="text-purple">Rafael</span></span></div>
            // </div>
        
    }

}