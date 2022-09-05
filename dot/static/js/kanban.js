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
        this.boards = []; // apontadores para os boards
        // Configuracao
        this.container = options?.container || document.body; // parentNode do kanban, createKanban(), caso nao informado append no body
        // Estilizacao
        this.kanbanClasslist = options?.kanbanClasslist || 'bg-light'; // classlist para o container principal
        this.boardClasslist = options?.boardClasslist || ''; // classlist para o board
        this.taskClasslist = options?.taskClasslist || ''; // classlist base para as tasks

        this.createKanban();
    }
    createKanban(){
        this.kanban = document.createElement('div');
        this.kanban.classList = this.kanbanClasslist;
        this.kanban.innerHTML = 'Meu Kanban';
        this.container.appendChild(this.kanban);
    }

}