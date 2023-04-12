/*
* addON.js  Classes com widgets de usuario
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
*/

class addOnAgenda{
    constructor(options){
        this.modal = null;
        this.events = {};
        this.table = null;
        this.view = 'new';
        this.btnShowOld = null;
        this.headers = ['date','hour','title'];
        this.addOnClasslist = options?.addOnClasslist || 'card-widget col-12 col-lg-8 col-xl-4 btn-dark pointer';
        this.eventClasslist = options?.eventClasslist || 'mb-1';

        this.start();
        this.createModal();
        this.getEvents();
    }
    start(){
        this.addOn = document.createElement('div');this.addOn.classList = this.addOnClasslist;
        this.addOn.onclick = () => {this.modal.show()};
        let title = document.createElement('span');title.classList = 'text-light';title.innerHTML = '<i class="fas fa-calendar-alt me-2"></i>Agenda Pessoal';
        this.list = document.createElement('ul');this.list.classList = 'list-unstyled fs-7 mt-1 mb-0';
        this.addOn.appendChild(title);
        this.addOn.appendChild(this.list);
        document.getElementById('messages_widget').before(this.addOn);
    }
    getEvents(){
        this.loading();
        dotAppData(`/app_data/core__agenda__{{user.id}}.json`).then((agenda) => {
            this.updateWidget(agenda); // Atualiza widget e tabela com dados da agenda
        });
    }
    createModal(){
        if(this.modal != null){return false;}
        let modal = document.createElement('div');modal.classList = 'modal fade';modal.tabIndex = '-1';
        let modalDialog = document.createElement('div');modalDialog.classList = `modal-dialog modal-lg`;
        let modalContent = document.createElement('div');modalContent.classList = 'modal-content';
        let modalBody = document.createElement('div');modalBody.classList = 'modal-body';
        let row = document.createElement('div');row.classList = 'row g-1'
        let col1 = document.createElement('div');col1.classList = 'col';
        let h6 = document.createElement('h6');h6.classList = 'text-body-secondary mb-3';h6.innerHTML = 'Editar Agenda';
        col1.appendChild(h6);
        let col2 = document.createElement('div');col2.classList = 'col-auto';
        let btnGroup = document.createElement('div');btnGroup.classList = 'btn-group fs-7';
        this.btnShowOld = document.createElement('button');this.btnShowOld.classList = 'btn btn-sm px-3 py-0 btn-outline-secondary';this.btnShowOld.title = 'Eventos Passados';this.btnShowOld.innerHTML = '<i class="fas fa-calendar-check"></i>';
        this.btnShowOld.onclick = () => {this.showPastEvents()}
        this.btnShowNew = document.createElement('button');this.btnShowNew.classList = 'btn btn-sm px-3 py-0 btn-outline-primary active';this.btnShowNew.title = 'Novos Eventos';this.btnShowNew.innerHTML = '<i class="far fa-calendar-alt"></i>';
        this.btnShowNew.onclick = () => { this.showNextEvents() }
        this.btnAddRow = document.createElement('button');this.btnAddRow.classList = 'btn btn-sm btn-success py-0 px-3 ms-1';this.btnAddRow.title = 'Adicionar Evento';this.btnAddRow.innerHTML = '<i class="fas fa-plus"></i>';
        this.btnAddRow.onclick = () => {
            this.table.addRow()
        }
        // ******************
        btnGroup.appendChild(this.btnShowOld);
        btnGroup.appendChild(this.btnShowNew);
        col2.appendChild(btnGroup);
        col2.appendChild(this.btnAddRow);
        row.appendChild(col1);
        row.appendChild(col2);
        modalBody.appendChild(row);
        // ******************
        let table_container = document.createElement('div');table_container.classList = 'table-responsive fs-7';
        this.tableEl = document.createElement('table');this.tableEl.id = 'addOnAgendaTable';this.tableEl.classList = 'table table-sm border table-striped table-hover mt-1';
        let thead = document.createElement('thead');
        let tr = document.createElement('tr');
        for(let i in this.headers){
            let td = document.createElement('td');td.innerHTML = this.headers[i];
            tr.appendChild(td);
        }
        thead.appendChild(tr);
        let tbody = document.createElement('tbody');
        this.tableEl.appendChild(thead);
        this.tableEl.appendChild(tbody);
        table_container.appendChild(this.tableEl);
        modalBody.appendChild(table_container);
        let modalFooter = document.createElement('div');modalFooter.classList = 'text-end mt-3';
        let modalBtnCancel = document.createElement('button');modalBtnCancel.classList = 'btn btn-sm btn-secondary';modalBtnCancel.setAttribute('data-bs-dismiss','modal');modalBtnCancel.innerHTML = 'Cancelar';
        modalBtnCancel.onclick = () => {this.showNextEvents()}
        let modalBtnAction = document.createElement('button');
        modalBtnAction.classList = 'btn btn-sm btn-primary ms-1';modalBtnAction.innerHTML = 'Gravar';
        modalBtnAction.onclick = () => {
            this.loading();
            this.updateEvents(); // Atualiza this.events com dados da tabela, descartando invalidos
            this.save(); // Salva no servidor dados da agenda
            this.updateWidget(); // Monta eventos no widget e table atualizados
            this.modal.hide();
        };
        modalFooter.appendChild(modalBtnCancel);
        modalFooter.appendChild(modalBtnAction);
        modalBody.appendChild(modalFooter);
        modalContent.appendChild(modalBody);
        modalDialog.appendChild(modalContent);
        modal.appendChild(modalDialog);
        document.body.appendChild(modal);
        this.modal = new bootstrap.Modal(modal, {keyboard: true});
        this.modal_created = true;
        
    }
    showNextEvents(){
        if(this.view == 'new'){return false;}
        this.view = 'new';
        this.events.old = this.table.getRows();
        if(this.events.new.length > 0){this.table.loadData(this.events.new)}
        else{this.table.cleanTbody();this.table.paginate();this.table.addEmptyRow();}
        this.btnShowNew.classList.add('active');
        this.btnShowOld.classList.remove('active');
    }
    showPastEvents(){
        if(this.view == 'old'){return false;}
        this.view = 'old';
        this.events.new = this.table.getRows();
        if(this.events.old.length > 0){this.table.loadData(this.events.old)}
        else{this.table.cleanTbody(); this.table.paginate();this.table.addEmptyRow();}
        this.btnShowNew.classList.remove('active');
        this.btnShowOld.classList.add('active');
    }
    updateWidget(agenda=this.events){ // Refaz lista do widget e linhas da tabela
        let countNextEvents = 0;
        let excedeuEventos = false;
        let translateDayWeek = {0:'Dom',1:'Seg',2:'Ter',3:'Qua',4:'Qui',5:'Sex',6:'Sab'};
        let translateMonth = {0:'Jan',1:'Fev',2:'Mar',3:'Abr',4:'Mai',5:'Jun',6:'Jul',7:'Ago',8:'Set',9:'Out',10:'Nov',11:'Dez'};
        let hoje = new Date();
        this.list.innerHTML = '';
        let ajustedOld = agenda.old || [];
        let ajustedNew = [];
        for(let item in agenda.new){
            let data = new Date(`${agenda.new[item].date} 23:00`);
            let prazo = dateDelta(data,hoje);
            if(countNextEvents == 4){excedeuEventos = true;continue;} // Mostra maximo de x eventos
            let event = document.createElement('li');event.classList = 'row g-1 pb-0 mb-1';
            if(prazo < 0){ajustedOld.push(agenda.new[item]);continue;}
            ajustedNew.push(agenda.new[item])
            if(prazo == 0){prazo = 'Hoje'}
            else if(prazo == 1){prazo = 'Amanhã'}
            event.innerHTML = `<div class="col-auto"><span style="border-radius: 20px;padding: 3px 4px; margin-right: 2px; background-color:#79589F; color:#FFF;font-size:0.7rem;font-weight:bold;font-family: monospace;">${agenda.new[item].date.slice(-2)}</span></div> `;
            event.innerHTML += `<div class="col-auto" style="font-family: monospace;">${translateMonth[data.getMonth()]}</div> `;
            event.innerHTML += `<div class="col-auto" style="color: #79589F;font-family: monospace;">${translateDayWeek[data.getDay()]}</div>`;
            event.innerHTML += `<div class="col text-truncate">${agenda.new[item].hour != '' ? '<span class="text-secondary-emphasis">' + agenda.new[item].hour + ' </span>' : ''}${agenda.new[item].title}</div>`;
            event.innerHTML += `<div class="col-auto"><small class="badge bg-purple-light ms-1 float-end">${prazo}</small></div>`;
            this.list.appendChild(event);
            countNextEvents++;
        }
        this.events = {old:ajustedOld,new:ajustedNew}; // Salva agenda na variavel global this.events
        if(this.table == null){ // Caso instancia jsTable ainda nao criada, inicia instancia
            this.table = new jsTable(this.tableEl, {
                canDeleteRow: true,
                canExportCsv:false,
                canSort:false,
                enablePaginate: true,
                rowsPerPage: 6,
                showCounterLabel:false,
                emptyTableMessage: 'Nenhum evento cadastrado',
                deleteRowButtonClasslist: 'pe-2 pointer',
                editableCols: ['date','hour','title']
            });
            if(this.events.new.length > 0){
                this.table.loadData(this.events.new)
            }
            this.table.table.querySelector('caption').remove();
        }
        else{ // Caso ja criado instancia jsTable, atualiza dados
            this.table.loadData(this.events[this.view]);
        }
        if(countNextEvents == 0){
            this.list.innerHTML = '<p>Nenhum evento cadastrado</p>';
            this.table.addEmptyRow();
        }
        else if(excedeuEventos){this.list.innerHTML += '<small>mais...</small>'}

    }
    updateEvents(){ // Atualiza this.events com dados da tabela
        this.events[this.view] = this.table.getRows(); // Atualiza dicionario com dados da tabela em exibicao (possivel alterada)
        // Ajusta eventos no old / new antes de salvar
        let hoje = new Date();
        let ajustedOld = [];
        let ajustedNew = [];
        for(let i in this.events.old){ // Percorre this.events.old movendo para new os com data >= hoje
            let data = new Date(`${this.events.old[i].date} 23:00`);
            if(isNaN(data) || this.events.old[i].date == ''){continue}; // Se data nao for valida, ignora entrada
            let prazo = dateDelta(data,hoje);
            if(prazo >= 0){ajustedNew.push(this.events.old[i])}
            else{ajustedOld.push(this.events.old[i])}
        }
        for(let i in this.events.new){ // Percorre this.events.new movendo para old os com data < hoje
            let data = new Date(`${this.events.new[i].date} 23:00`);
            if(isNaN(data) || this.events.new[i].date == ''){continue}; // Se data nao for valida, ignora entrada
            let prazo = dateDelta(data,hoje);
            if(prazo < 0){ajustedOld.push(this.events.new[i])}
            else{ajustedNew.push(this.events.new[i])}
        }
        // Reordena por data os arrays new e old
        let sortedOld = ajustedOld.sort((a, b) => {return a.date > b.date ? 1 : -1;});
        let sortedNew = ajustedNew.sort((a, b) => {return a.date > b.date ? 1 : -1;});
        this.events.old = sortedOld;
        this.events.new = sortedNew;
        
    }
    save(){ // Faz upload dos dados salvos
        dotAppDataUpdate({ // Atualiza no server a agenda com alteracoes
            url:'/app_data/core__agenda__{{user.id}}.json',
            data:JSON.stringify(this.events),
            onSuccess: () => {
                this.modal.hide(); // Oculta Modal bootstrap
                this.showNextEvents() // Muda visualizacao (caso nao esteja) para o new
            },
            showSuccessAlert:false
        }); // Ajusta json no server com dados da agenda
    }
    destroy(){
        this.addOn.remove();
        this.modal._element.remove();
    }
    loading(){
        this.list.innerHTML = '<li><div class="text-center"><div class="spinner-border text-success"></div></div></li>';
    }
}

class addOnTarefas{
    constructor(options){
        this.tasks = {};
        // *****************
        this.start();
        this.getTasks();
    }
    start(){
        this.addOn = document.createElement('div');this.addOn.classList = 'card-widget col-12 col-lg-4 col-xl-2 bg-dark text-light';
        let header = document.createElement('div');header.classList = 'row mb-2';
        let col1 = document.createElement('div');col1.classList = 'col';col1.innerHTML = '<i class="fas fa-list me-2"></i>Tarefas';
        let col2 = document.createElement('div');col2.classList = 'col-auto';
        this.btnSave = document.createElement('span');this.btnSave.classList = 'btn btn-sm btn-phanton-light';this.btnSave.innerHTML = '<i class="fas fa-save"></i>';
        this.btnSave.onclick = () => {this.save();};
        this.btnAddTask = document.createElement('span');this.btnAddTask.classList = 'btn btn-sm btn-phanton-light';this.btnAddTask.innerHTML = '<i class="fas fa-plus"></i>';
        this.btnAddTask.onclick = () => {this.addTask()};
        col2.appendChild(this.btnSave);
        col2.appendChild(this.btnAddTask);
        header.appendChild(col1);
        header.appendChild(col2);
        let addOnTarefa_container = document.createElement('div');addOnTarefa_container.classList = 'container-fluid p-1';addOnTarefa_container.style = 'max-height: 150px;overflow-y: scroll;';
        this.list = document.createElement('ul');this.list.classList = 'list-unstyled fs-7 mt-1 mb-0';
        addOnTarefa_container.appendChild(this.list);
        this.addOn.appendChild(header);
        this.addOn.appendChild(addOnTarefa_container);
        document.getElementById('messages_widget').before(this.addOn);
    }
    getTasks(){
        this.loading();
        dotAppData(`/app_data/core__tarefa__{{user.id}}.json`).then((obj) => {
            this.list.innerHTML = '';
            this.tasks = obj;
            for(let item in obj){
                let event = document.createElement('li');event.classList = 'dotTarefa-event row g-1 pb-0';
                let controlDiv = document.createElement('div');controlDiv.classList = 'col-auto';
                let textDiv = document.createElement('div');textDiv.classList = 'col dotTarefa-title text-truncate';
                let checkbox = document.createElement('input');checkbox.type = "checkbox";checkbox.classList = 'form-check-input me-1';
                let label = document.createElement('div');label.classList = 'pointer user-select-none';label.innerHTML = obj[item].title;
                label.ondblclick = () => {
                    label.style.display = 'none';
                    let input = document.createElement('input');input.value = label.innerText;input.classList = 'form-control form-control-sm fs-8 py-0';input.style.minHeight = '20px';
                    label.after(input);
                    input.onblur = () => {
                        if(input.value.trim() != ''){
                            label.innerHTML = input.value;
                            label.style.display = 'block';
                            input.remove();
                        }
                        else{ // Se texto vazio inserido remove o item
                            event.remove();
                            if(this.list.childElementCount == 0){this.list.innerHTML = '<p>Nenhuma tarefa adicionada</p>';}
                        }
                    };
                    input.onkeydown = (e) => {if(e.key == 'Enter'){input.blur();}}
                    input.select();
                };
                checkbox.onclick = () => {
                    if(checkbox.checked){label.classList.add('text-decoration-line-through','fst-italic','text-body-secondary');}
                    else{label.classList.remove('text-decoration-line-through','fst-italic','text-body-secondary');}
                }
                controlDiv.appendChild(checkbox)
                textDiv.appendChild(label);
                event.appendChild(controlDiv);
                event.appendChild(textDiv);
                this.list.appendChild(event);
            }
            if(this.tasks.length == 0){this.list.innerHTML = '<p>Nenhuma tarefa adicionada</p>';}
        });
    }
    save(){
        let tarefas = [];
        this.list.querySelectorAll('input[type=checkbox]').forEach((e) => {
            if(e.checked){e.parentNode.parentNode.remove()}
            else{tarefas.push({title:e.parentNode.parentNode.childNodes[1].innerText})}
        });
        dotAppDataUpdate({url:'/app_data/core__tarefa__{{user.id}}.json',data:JSON.stringify(tarefas),onSuccessMsg:'Tarefas <b>salvas</b>'});
        if(tarefas.length == 0){this.list.innerHTML = '<p>Nenhuma tarefa adicionada</p>'}
    }
    destroy(){this.addOn.remove();}
    addTask(){
        this.list.querySelectorAll('p').forEach((e) => {e.remove()}); // Remove texto de (Nenhuma tarefa ....) caso exista
        let event = document.createElement('li');event.classList = 'dotTarefa-event row g-1 pb-0';
        let controlDiv = document.createElement('div');controlDiv.classList = 'col-auto';
        let textDiv = document.createElement('div');textDiv.classList = 'col dotTarefa-title text-truncate';
        let checkbox = document.createElement('input');checkbox.type = "checkbox";checkbox.classList = 'form-check-input me-1';
        let label = document.createElement('div');label.classList = 'pointer user-select-none';label.innerHTML = 'nova tarefa...';
        label.ondblclick = () => {
            label.style.display = 'none';
            let input = document.createElement('input');input.value = label.innerText;input.classList = 'form-control form-control-sm fs-8 py-0';input.style.minHeight = '20px';
            label.after(input);
            input.onblur = () => {
                if(input.value.trim() != ''){
                    label.innerHTML = input.value;
                    label.style.display = 'block';
                    input.remove();
                }
                else{ // Se texto vazio inserido remove o item
                    event.remove();
                    if(this.list.childElementCount == 0){this.list.innerHTML = '<p>Nenhuma tarefa adicionada</p>';}
                }
            };
            input.onkeydown = (e) => {if(e.key == 'Enter'){input.blur();}}
            input.select();
        };
        checkbox.onclick = () => {
            if(checkbox.checked){label.classList.add('text-decoration-line-through','fst-italic','text-body-secondary');}
            else{label.classList.remove('text-decoration-line-through','fst-italic','text-body-secondary');}
        }
        controlDiv.appendChild(checkbox)
        textDiv.appendChild(label);
        event.appendChild(controlDiv);
        event.appendChild(textDiv);
        this.list.appendChild(event);
    }
    loading(){
        this.list.innerHTML = '<li><div class="text-center"><div class="spinner-border text-success"></div></div></li>';
    }
}

var addOn_agenda = null;
var addOn_tarefas = null;
const models = {'addOnAgenda':addOnAgenda,'addOnTarefas':addOnTarefas}
function addOnSettingsChange(el){
    localStorage.setItem(el.name, el.checked); // Altera valor da entrada referente ao addon no localStorage
    if(el.checked){
        if(window[el.name] == null){window[el.name] = new models[el.dataset.model]();}
    }
    else{
        window[el.name].destroy();
        window[el.name] = null;
    }

}

// *******************************
// Onload Calls

if(localStorage.addOn_agenda == 'true'){
    document.getElementById('id_addOnAgenda').checked = true;
    addOn_agenda = new addOnAgenda({});
}
if(localStorage.addOn_tarefas == 'true'){
    document.getElementById('id_addOnTarefas').checked = true;
    addOn_tarefas = new addOnTarefas({});
}