class jsKB_Board{
    constructor(options){}
}

class jsKB_Task{
    constructor(options){}
}

class Kanban{
    constructor(options){
        // Variaveis internas
        this.kanban = null; // container pai, contem todos os boards
        this.header = null; // container dos headers (id, pesquisa, etc)
        this.body = null; // container do corpo do kanban (boards)
        this.nav = null; // nav para filtro e navegacao das tasks
        // Configuracao
        // this.boards = options?.data || []; // Json com dados dos boards kanban
        this.container = options?.container || document.body; // parentNode do kanban, createKanban(), caso nao informado append no body
        this.sortableOptions = options?.sortableOptions || {}; // options da instancia Sortable JS
        // Estilizacao
        this.kanbanClasslist = options?.kanbanClasslist || 'bg-light'; // classlist para o container principal
        this.navClasslist = options?.navClasslist || ''; // classlist para o nav
        this.bodyClasslist = options?.bodyClasslist || ''; // classlist para o board
        this.boardClasslist = options?.boardClasslist || 'col-2 bg-secondary'; // classlist para o board
        this.taskClasslist = options?.taskClasslist || ''; // classlist base para as tasks

        this.createKanban();
        this.buildNav();
        this.addBoard();
    }
    createKanban(){
        this.kanban = document.createElement('div');
        this.kanban.classList = this.kanbanClasslist;
        let row = document.createElement('div');
        row.classList = 'row';
        this.header = document.createElement('div');
        this.header.classList = 'col-12 bg-info';
        this.header.innerHTML = 'HEADER';
        let nav_container = document.createElement('div');
        nav_container.classList = 'col-auto pt-3 ps-2 pe-5 bg-success';
        nav_container.innerHTML = 'NAV';
        this.body = document.createElement('div');
        this.body.classList = 'col p-3 bg-warning';
        row.appendChild(this.header);
        row.appendChild(nav_container);
        row.appendChild(this.body);
        this.kanban.appendChild(row);
        this.container.appendChild(this.kanban);
    }
    buildNav(){}
    addBoard(options){
        let board = document.createElement('div');
        board.classList = this.boardClasslist;
        let header = document.createElement('div');
        header.classList = 'row';
        let header_name = document.createElement('div');
        header_name.classList = 'col';
        header_name.innerHTML = `<h6>${options?.title || 'Novo grupo'}</h6>`;
        let header_controls = document.createElement('div');
        header.appendChild(header_name);
        header.appendChild(header_controls);
        let dnd_container = document.createElement('div');
        dnd_container.classList = 'bg-dark';
        dnd_container.style.minHeight = '120px';
        new Sortable(dnd_container,this.sortableOptions);
        board.appendChild(header);
        board.appendChild(dnd_container);
        this.body.appendChild(board);
    }
    addTask(dnd_container){
        
    }

}