/*
* addON.js  Classes com widgets de usuario
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
*/

class addOnAgenda{
    constructor(options){
        // this.enter = options?.enter || !options.enter == undefined;
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
    loading(){
        this.list.innerHTML = '<li><div class="text-center"><div class="spinner-border text-success"></div></div></li>';
    }
}

class addOnTarefas{
    constructor(options){}
    start(){}
    addEvent(){}
    getTasks(){}
}


const addon_agenda = new addOnAgenda();