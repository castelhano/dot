/* Escopo
dotGetUserProfileConfig()       # Busca profile do usuario logado
dotSaveUserProfileConfig()      # Salva profile ao clicar botao Gravar (offcanvas)
addOnAgenda_start()             # Cria o widget da agenda e chama addOnAgenda_update() e addOnAgenda_modal_create()
addOnAgenda_update()            # Busca dados da agenda do usuario
addOnAgenda_modal_create()      # Cria modal para edicao dos eventos da agenda
addOnTarefa_start()            # Cria o widget para tarefas e chama addOnTarefa_update() e addOnTarefa_modal_create()
addOnTarefa_update()            # Busca dados das tarefas do usuario
**********************
addOnAgenda_agenda              # Aponta para dicionario com agenda do usuario
addOnAgenda_table               # Instancia jsTable da agenda
addOnAgenda_modal               # Instancia modal bootstrap
addOnAgenda_list                      # Lista (ul) com eventos da agenda (mostrados no widget)
addOnAgenda_modal_created       # Booleado define se modal foi criado
addOnAgenda_modal_view          # String define se view esta em eventos futuros ou passados 'new' ou 'old'


*/
function dotGetUserProfileConfig(){
    dotAppData(`/app_data/core__user_settings__{{user.id}}.json`).then((d) => {
        if(d == ''){ // Caso nao tenha arquivo de configuracao, inicia e salva
            let defaultOptions = {
                addOnAgenda: false,
                addOnTarefas: false
            }
            dotAppDataUpdate({url:'/app_data/core__user_settings__{{user.id}}.json',data:JSON.stringify(defaultOptions),onSuccessMsg:'Arquivo de <b>configurações iniciado</b>'});
        }
        else{
            document.getElementById('id_addOnAgenda').checked = d.addOnAgenda;
            document.getElementById('id_addOnTarefas').checked = d.addOnTarefas;
            if(d.addOnAgenda){addOnAgenda_start();}
            if(d.addOnTarefas){addOnTarefa_start();}
        }
    });
}
dotGetUserProfileConfig();

function dotSaveUserProfileConfig(options=null){
    let settings = options || {
        addOnAgenda: document.getElementById('id_addOnAgenda').checked,
        addOnTarefas: document.getElementById('id_addOnTarefas').checked
    }
    dotAppDataUpdate({
        url:'/app_data/core__user_settings__{{user.id}}.json',
        data:JSON.stringify(settings),
        showSuccessAlert:false,
        onSuccessMsg:'<b>dot</b>: Configurações salvas',
        onSuccess: ()=>{
            document.getElementById('offCanvasLink').click();
            document.getElementById('clear').click();
        }
    });
}

var addOnAgenda_list = null;
function addOnAgenda_start(){
    let addOn = document.createElement('div');addOn.classList = 'card-widget col-12 col-lg-8 col-xl-4 btn-dark pointer';
    addOn.onclick = () => {addOnAgenda_modal.toggle()};
    let addOn_title = document.createElement('span');addOn_title.classList = 'text-light';addOn_title.innerHTML = '<i class="fas fa-calendar-alt me-2"></i>Agenda';
    addOnAgenda_list = document.createElement('ul');addOnAgenda_list.classList = 'list-unstyled fs-7 mt-1 mb-0';
    addOnAgenda_modal_create();
    addOnAgenda_update(addOnAgenda_list);  
    addOn.appendChild(addOn_title);
    addOn.appendChild(addOnAgenda_list);
    document.getElementById('messages_widget').before(addOn);
}

var addOnAgenda_agenda = {};
var addOnAgenda_table = null;
function addOnAgenda_update(){
    addOnAgenda_list.innerHTML = '<li><div class="text-center"><div class="spinner-border text-success"></div></div></li>';
    dotAppData(`/app_data/core__agenda__{{user.id}}.json`).then((agenda) => {
        let countNextEvents = 0;
        let excedeuEventos = false;
        let translateDayWeek = {0:'Dom',1:'Seg',2:'Ter',3:'Qua',4:'Qui',5:'Sex',6:'Sab'};
        let translateMonth = {0:'Jan',1:'Fev',2:'Mar',3:'Abr',4:'Mai',5:'Jun',6:'Jul',7:'Ago',8:'Set',9:'Out',10:'Nov',11:'Dez'};
        let hoje = new Date();
        addOnAgenda_list.innerHTML = '';
        for(let item in agenda.new){
            let data = new Date(`${agenda.new[item].date} 23:00`);
            let prazo = dateDelta(data,hoje);
            if(countNextEvents == 4){excedeuEventos = true;continue;} // Mostra maximo de x eventos
            let event = document.createElement('li');event.classList = 'dotAgenda-event row g-1 pb-0';
            if(prazo == 0){prazo = 'Hoje'};
            event.innerHTML = `<div class="col-auto"><span class="dotAgenda-data-dia">${agenda.new[item].date.slice(-2)}</span></div> `;
            event.innerHTML += `<div class="col-auto dotAgenda-data-mes">${translateMonth[data.getMonth()]}</div> `;
            event.innerHTML += `<div class="col-auto dotAgenda-data-dayWeek">${translateDayWeek[data.getDay()]}</div>`;
            event.innerHTML += `<div class="col dotAgenda-title text-truncate">${agenda.new[item].title}</div>`;
            event.innerHTML += `<div class="col-auto"><small class="badge bg-purple-light ms-1 float-end">${prazo}</small></div>`;
            addOnAgenda_list.appendChild(event);
            countNextEvents++;
        }
        addOnAgenda_agenda = agenda || {old:[],new:[]}; // Salva agenda na variavel global addOnAgenda_agenda
        if(addOnAgenda_table == null){ // Caso instancia jsTable ainda nao criada, inicia instancia
            addOnAgenda_table = new jsTable(document.getElementById('addOnAgenda_table_el'), {
                canDeleteRow: true,
                canExportCsv:false,
                canSort:false,
                showCounterLabel:false,
                emptyTableMessage: 'Nenhum evento cadastrado',
                editableColsClasslist: 'text-muted',
                deleteRowButtonClasslist: 'pe-2 pointer',
                editableCols: ['date','hour','title']
            });
            if(addOnAgenda_agenda.new.length > 0){addOnAgenda_table.data = [];addOnAgenda_table.raw = [];addOnAgenda_table.appendData(addOnAgenda_agenda.new)}
            addOnAgenda_table.table.querySelector('caption').remove();
        }
        else{ // Caso ja criado instancia jsTable, atualiza dados
            addOnAgenda_table.data = [];addOnAgenda_table.raw = [];
            addOnAgenda_table.appendData(addOnAgenda_agenda[addOnAgenda_modal_view]);
        }
        if(countNextEvents == 0){
            addOnAgenda_list.innerHTML = '<p>Nenhum evento cadastrado</p>';
            addOnAgenda_table.addEmptyRow();
        }
        else if(excedeuEventos){addOnAgenda_list.innerHTML += '<small>mais...</small>'}
    });
}

var addOnAgenda_modal = null;
var addOnAgenda_modal_created = false;
var addOnAgenda_modal_view = 'new';
function addOnAgenda_modal_create(options){
    if(addOnAgenda_modal_created){return false;}
    let modal = document.createElement('div');modal.classList = 'modal fade';modal.tabIndex = '-1';
    let modalDialog = document.createElement('div');modalDialog.classList = `modal-dialog modal-lg`;
    let modalContent = document.createElement('div');modalContent.classList = 'modal-content';
    let modalBody = document.createElement('div');modalBody.classList = 'modal-body';
    modalBody.innerHTML = `<div class="row g-1"><div class="col"><h6 class="text-muted mb-3">Editar Agenda<h6></div><div class="col-auto"><div class="btn-group fs-7" role="group"><button type="button" data-type="addOnAgendaBtnShowOld" class="btn btn-sm px-3 py-0 btn-outline-secondary" title="Eventos Passados" onclick="addOnAgenda_showOld()"><i class="fas fa-calendar-check"></i></button><button type="button" data-type="addOnAgendaBtnShowNew" class="btn btn-sm px-3 py-0 btn-outline-primary active" title="Novos Eventos" onclick="addOnAgenda_showNew()"><i class="far fa-calendar-alt"></i></button></div><button class="btn btn-sm btn-success py-0 px-3 ms-1" onclick="addOnAgenda_table.addRow();"><i class="fas fa-plus"></i></button></div></div>`;
    modalBody.innerHTML += `<div class="table-responsive"><table id="addOnAgenda_table_el" class="table table-sm border table-striped table-hover mt-1"><thead><tr><th>date</th><th>hour</th><th>title</th></tr></thead><tbody></tbody></table></div>`;
    let modalFooter = document.createElement('div');modalFooter.classList = 'text-end mt-3';
    let modalBtnCancel = document.createElement('button');modalBtnCancel.classList = 'btn btn-sm btn-secondary';modalBtnCancel.setAttribute('data-bs-dismiss','modal');modalBtnCancel.innerHTML = 'Cancelar';
    modalBtnCancel.onclick = () => {addOnAgenda_showNew()}
    let modalBtnAction = document.createElement('button');modalBtnAction.setAttribute('data-type', 'modalAction');
    modalBtnAction.classList = 'btn btn-sm btn-primary ms-1';modalBtnAction.innerHTML = 'Gravar';
    modalBtnAction.onclick = () => {
        addOnAgenda_list.innerHTML = '<li><div class="text-center"><div class="spinner-border text-success"></div></div></li>';
        addOnAgenda_agenda[addOnAgenda_modal_view] = addOnAgenda_table.getRows(); // Atualiza dicionario com dados da tabela em exibicao (possivel alterada)
        // Ajusta eventos no old / new antes de salvar
        let hoje = new Date();
        let ajustedOld = [];
        let ajustedNew = [];
        for(let i in addOnAgenda_agenda.old){ // Percorre addOnAgenda_agenda.old movendo para new os com data >= hoje
            let data = new Date(`${addOnAgenda_agenda.old[i].date} 23:00`);
            if(isNaN(data)){continue}; // Se data nao for valida, ignora entrada
            let prazo = dateDelta(data,hoje);
            if(addOnAgenda_agenda.old[i].date == ''){continue}; // Descarta entrada com data vazia
            if(prazo >= 0){ajustedNew.push(addOnAgenda_agenda.old[i])}
            else{ajustedOld.push(addOnAgenda_agenda.old[i])}
        }
        for(let i in addOnAgenda_agenda.new){ // Percorre addOnAgenda_agenda.new movendo para old os com data < hoje
            let data = new Date(`${addOnAgenda_agenda.new[i].date} 23:00`);
            if(isNaN(data)){continue}; // Se data nao for valida, ignora entrada
            let prazo = dateDelta(data,hoje);
            if(addOnAgenda_agenda.new[i].date == ''){continue}; // Descarta entrada com data vazia
            if(prazo < 0){ajustedOld.push(addOnAgenda_agenda.new[i])}
            else{ajustedNew.push(addOnAgenda_agenda.new[i])}
        }
        // Reordena por data os arrays new e old
        let sortedOld = ajustedOld.sort((a, b) => {return a.date > b.date ? 1 : -1;});
        let sortedNew = ajustedNew.sort((a, b) => {return a.date > b.date ? 1 : -1;});
        addOnAgenda_agenda.old = sortedOld;
        addOnAgenda_agenda.new = sortedNew;
        // ***************************************
        dotAppDataUpdate({ // Atualiza no server a agenda com alteracoes
            url:'/app_data/core__agenda__{{user.id}}.json',
            data:JSON.stringify(addOnAgenda_agenda),
            onSuccess: () => {
                addOnAgenda_modal.hide(); // Oculta Modal bootstrap
                addOnAgenda_update(); // Atualiza eventos no widget e modal
                addOnAgenda_showNew() // Muda visualizacao (caso nao esteja) para o new
            },
            showSuccessAlert:false
        }); // Ajusta json no server com dados da agenda
    };
    
    modalFooter.appendChild(modalBtnCancel);
    modalFooter.appendChild(modalBtnAction);
    modalBody.appendChild(modalFooter);
    modalContent.appendChild(modalBody);
    modalDialog.appendChild(modalContent);
    modal.appendChild(modalDialog);
    document.body.appendChild(modal);
    addOnAgenda_modal = new bootstrap.Modal(modal, {keyboard: true});
    addOnAgenda_modal_created = true;
}

function addOnAgenda_showOld(){
    if(addOnAgenda_modal_view == 'old'){return false;}
    addOnAgenda_modal_view = 'old';
    addOnAgenda_agenda.new = addOnAgenda_table.getRows();
    addOnAgenda_table.data = [];addOnAgenda_table.raw = [];
    if(addOnAgenda_agenda.old.length > 0){addOnAgenda_table.appendData(addOnAgenda_agenda.old)}
    else{addOnAgenda_table.cleanTbody();addOnAgenda_table.addEmptyRow();}
    document.querySelector('[data-type=addOnAgendaBtnShowNew]').classList.remove('active');
    document.querySelector('[data-type=addOnAgendaBtnShowOld]').classList.add('active');
}
function addOnAgenda_showNew(){
    if(addOnAgenda_modal_view == 'new'){return false;}
    addOnAgenda_modal_view = 'new';
    addOnAgenda_agenda.old = addOnAgenda_table.getRows();
    addOnAgenda_table.data = [];addOnAgenda_table.raw = [];
    if(addOnAgenda_agenda.new.length > 0){addOnAgenda_table.appendData(addOnAgenda_agenda.new)}
    else{addOnAgenda_table.cleanTbody();addOnAgenda_table.addEmptyRow();}
    document.querySelector('[data-type=addOnAgendaBtnShowNew]').classList.add('active');
    document.querySelector('[data-type=addOnAgendaBtnShowOld]').classList.remove('active');
}

var addOnTarefa_list = null;
function addOnTarefa_start(){
    let addOn = document.createElement('div');addOn.classList = 'card-widget col-6 col-lg-4 col-xl-2 bg-dark text-light';
    let addOn_title = document.createElement('span');addOn_title.classList = 'text-light';addOn_title.innerHTML = '<i class="fas fa-list me-2"></i>Tarefas';
    let addOnTarefa_container = document.createElement('div');addOnTarefa_container.classList = 'container-fluid p-1';addOnTarefa_container.style = 'max-height: 150px;overflow-y: scroll;';
    addOnTarefa_list = document.createElement('ul');addOnTarefa_list.classList = 'list-unstyled fs-7 mt-1 mb-0';
    addOnTarefa_update(addOnTarefa_list);  
    addOnTarefa_container.appendChild(addOnTarefa_list);
    addOn.appendChild(addOn_title);
    addOn.appendChild(addOnTarefa_container);
    document.getElementById('messages_widget').before(addOn);
}

var addOnTarefa_tarefas = null;
function addOnTarefa_update(){
    addOnTarefa_list.innerHTML = '<li><div class="text-center"><div class="spinner-border text-success"></div></div></li>';
    dotAppData(`/app_data/core__tarefa__{{user.id}}.json`).then((obj) => {
        addOnTarefa_list.innerHTML = '';
        addOnTarefa_tarefas = obj;
        for(let item in obj){
            let event = document.createElement('li');event.classList = 'dotTarefa-event row g-1 pb-0';
            let controlDiv = document.createElement('div');controlDiv.classList = 'col-auto';
            let textDiv = document.createElement('div');textDiv.classList = 'col dotTarefa-title text-truncate';
            let checkbox = document.createElement('input');checkbox.type = "checkbox";checkbox.classList = 'form-check-input me-1';checkbox.id = `addOnTarefa__${item}`;
            let label = document.createElement('label');label.classList = 'form-check-label';label.setAttribute('for',`addOnTarefa__${item}`);label.innerHTML = obj[item].title;
            checkbox.onclick = () => {
                if(checkbox.checked){label.classList.add('text-decoration-line-through','fst-italic','text-muted');}
                else{label.classList.remove('text-decoration-line-through','fst-italic','text-muted');}
            }
            controlDiv.appendChild(checkbox)
            textDiv.appendChild(label);
            event.appendChild(controlDiv);
            event.appendChild(textDiv);
            addOnTarefa_list.appendChild(event);
        }
        if(addOnTarefa_tarefas.length == 0){
            addOnTarefa_list.innerHTML = '<p>Nenhum evento cadastrado</p>';
        }
    });
}