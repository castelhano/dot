/*
* jsCalendar   Implementa componte de calendario
*
* @version  1.05
* @since    23/01/2023
* @release  30/01/2023 [adicionado visao de tarefas]
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com}
* @depend   boostrap 5.2.0, fontawesome 5.15.4, dot.css, dot.js
*/

class jsCalendar{
    constructor(options){
        this.today = new Date();
        this.year = options?.year || this.today.getFullYear();
        this.month = options?.month > 0 && options?.month < 13 ? options?.month : false || this.today.getMonth() + 1;
        this.monthNames = options?.monthNames || ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        this.summary = {'uteis':0, 'sabados':0, 'domingos':0, 'feriados':0};
        this.summaryEl = null;
        this.selectedDays = options?.selectedDays || [];
        // --------------------------
        this.container = options?.container || document.body; // parentNode do calendario, caso nao informado append no body
        this.view = options?.view || 'calendar'; // define tipo de vizualizacao ['calendar','tasks']
        if(!['calendar','tasks'].includes(this.view)){this.view = 'calendar'}; // se repassado view invalido, ajusta para view default
        this.holidays = options?.holidays || {}; // Dicionario com os feriados no período
        this.events = options?.events || {}; // Armazena json com os eventos, exige dia como ocupado
        this.yearMin = options?.yearMin || 1500; // Define ano minimo para pesquisa (ignora valores menores)
        this.yearMax = options?.yearMax || 2999; // Define ano maximo para pesquisa (ignora valores maiores)
        this.showSummary = options?.showSummary != undefined ? options.showSummary : false; // Booleano defini se sera exibido resumo da quantidade de dias por tipo (util, sab, dom, etc..)
        this.canChangeView = options?.canChangeView != undefined ? options.canChangeView : true; // Booleano defini sera exibido botao para mudar view (calendario, tarefas)
        this.onclick = options?.onclick != undefined ? options.onclick : false; // Funcao definida aqui sera acionada no evento click do calendario, repassando o dia clicado
        this.onchange = options?.onchange != undefined ? options.onchange : false; // Funcao definida aqui sera acionada sempre apos o calendarRebuild() 
        this.canSelectDay = options?.canSelectDay != undefined ? options.canSelectDay : false; // Booleano defini se as datas sao selecionaveis
        this.multiSelect = options?.multiSelect != undefined ? options.multiSelect : false; // Booleano defini se eh permitido multipla seleao de dias
        this.wait = options?.wait != undefined ? options.wait : false; // Booleano, se true nao chama funcao calendarRebuild()
        // --------------------------
        this.calendarClasslist = options?.calendarClasslist || 'table table-sm border caption-top text-center mb-1 user-select-none fs-9'; // classlist do calendar
        this.captionClasslist =  options?.captionClasslist || 'py-1'; // classlist do caption
        this.headerClasslist = options?.headerClasslist || 'border'; // classlist do cabecalho
        this.monthNameClassList = options?.monthNameClassList || 'mt-0 pointer fs-6'; // classlist do h5 com o nome do mes
        this.monthPickerClassList = options?.monthPickerClassList || 'form-select form-select-sm me-1 fs-9'; // classlist do select para mes
        this.yearPickerClassList = options?.yearPickerClassList || 'form-control form-control-sm me-1 fs-9'; // classlist do input number para ano
        this.taskListClasslist = options?.taskListClasslist || 'list-unstyled fs-7'; // classlist da lista de eventos (ul)
        this.customDayClasslist = options?.customDayClasslist || 'border py-1 bg-light fs-7'; // classlist de dia padrao
        this.holidayClasslist = options?.holidayClasslist || 'border py-1 bg-danger-light fs-7'; // classlist do feriado
        this.busyDayClasslist = options?.busyDayClasslist || 'border py-1 bg-purple-light fs-7'; // classlist de dia com evento (busy day)
        this.emptyDayClasslist = options?.emptyDayClasslist || 'border py-1'; // classlist do calendar
        this.selectDayClasslist = options?.selectDayClasslist || 'border py-1 bg-warning fs-7'; // classlist do btn para selecionar dia
        this.calendarControlsChangeViewClasslist = options?.calendarControlsChangeViewClasslist || 'btn btn-sm btn-secondary fs-8 me-1 py-1 py-lg-0';
        this.calendarControlsCurrentClasslist = options?.calendarControlsCurrentClasslist || 'btn btn-sm btn-secondary fs-8 me-1 py-1 py-lg-0'; // classlist dos controles de navegacao
        this.calendarControlsNavegateClasslist = options?.calendarControlsNavegateClasslist || 'btn btn-sm btn-light fs-8 py-1 py-lg-0'; // classlist dos controles de navegacao
        this.calendarControlsCancelClasslist = options?.calendarControlsCancelClasslist || 'btn btn-sm btn-secondary fs-9 me-1'; // classlist do botao cancelar escolha de dia
        this.calendarControlsSelectDayClasslist = options?.calendarControlsSelectDayClasslist || 'btn btn-sm btn-primary fs-9'; // classlist do botao selecionar dia
        this.taskContainerClassList = options?.taskContainerClassList || ''; // classlist do container das tasks

        // --------------------------
        this.createCalendar();
        if(this.onclick){this.__configureCssClass();} // Adiciona classes adicionais caso informado evento onclick
        if(!this.wait){this.calendarRebuild(true)}
    }
    __configureCssClass(){
        let style = document.createElement('style');
        style.innerHTML = '[data-date]:hover{box-shadow: inset 1px 1px 7px 7px rgba(158,155,158,0.2);}';
        document.getElementsByTagName('head')[0].appendChild(style);
    }
    createCalendar(){
        this.calendar = document.createElement('table');this.calendar.classList = this.calendarClasslist;this.calendar.style.tableLayout = 'fixed';
        let caption = document.createElement('caption');caption.classList = this.captionClasslist;
        let row = document.createElement('div');row.classList = 'row align-items-end g-1';
        let td1 = document.createElement('div');td1.classList = 'col d-flex align-items-start';
        let td2 = document.createElement('div');td2.classList = 'col-auto';
        this.monthName = document.createElement('h5');this.monthName.classList = this.monthNameClassList;this.monthName.style.marginBlockEnd = '0px';
        this.monthName.onclick = () => { // Quando clicado no nome do ano, exibe controles para escolher ano/mes
            this.monthName.classList.add('d-none');
            td2.classList.add('d-none');
            this.monthPicker = document.createElement('select');this.monthPicker.classList = this.monthPickerClassList;
            for(let i = 1;i <= this.monthNames.length;i++){
                let opt = document.createElement('option');
                opt.value = i;opt.innerHTML = this.monthNames[i-1].toUpperCase();
                this.monthPicker.appendChild(opt);
            }
            this.monthPicker.value = this.month; // Inicia o select com o mes em foco
            this.yearPicker = document.createElement('input');this.yearPicker.type = 'number';this.yearPicker.min = this.yearMin;this.yearPicker.max = this.yearMax;this.yearPicker.classList = this.yearPickerClassList;
            this.yearPicker.value = this.year;
            this.btnSelectDate = document.createElement('button');this.btnSelectDate.type = 'button';this.btnSelectDate.classList = this.calendarControlsSelectDayClasslist;this.btnSelectDate.style.width = '70px';this.btnSelectDate.innerHTML = '<i class="fas fa-arrow-right"></i>';
            this.btnSelectDate.onclick = () => {
                this.year = this.yearPicker.value >= this.yearMin && this.yearPicker.value <= this.yearMax ? this.yearPicker.value : this.year;
                this.month = this.monthPicker.value;
                this.goTo(this.year,this.month);
                this.btnCancelSelectDate.click();
            };
            this.btnCancelSelectDate = document.createElement('button');this.btnCancelSelectDate.type = 'button';this.btnCancelSelectDate.classList = this.calendarControlsCancelClasslist;this.btnCancelSelectDate.style.width = '70px';this.btnCancelSelectDate.innerHTML = '<i class="fas fa-times"></i>';
            this.btnCancelSelectDate.onclick = () => {
                this.monthPicker.remove();
                this.yearPicker.remove();
                this.btnSelectDate.remove();
                this.btnCancelSelectDate.remove();
                this.monthName.classList.remove('d-none');
                td2.classList.remove('d-none');
            };
            td1.appendChild(this.monthPicker);
            td1.appendChild(this.yearPicker);
            td1.appendChild(this.btnCancelSelectDate);
            td1.appendChild(this.btnSelectDate);
        }
        td1.appendChild(this.monthName);
        // Contruindo os controles de navegacao do calendario
        if(this.canChangeView){
            this.changeViewBtn = document.createElement('button');this.changeViewBtn.type = 'button';this.changeViewBtn.classList = this.calendarControlsChangeViewClasslist;this.changeViewBtn.style.width = '40px';this.changeViewBtn.innerHTML = this.view == 'calendar' ? '<i class="fas fa-list-ul"></i>' : '<i class="fas fa-calendar-alt"></i>';
            this.changeViewBtn.onclick = () => this.changeView();
            td2.appendChild(this.changeViewBtn);
        }
        this.currentMonthBtn = document.createElement('button');this.currentMonthBtn.type = 'button';this.currentMonthBtn.classList = this.calendarControlsCurrentClasslist;this.currentMonthBtn.innerHTML = 'Hoje';
        this.currentMonthBtn.onclick = () => this.currentMonth();
        this.previousMonthBtn = document.createElement('button');this.previousMonthBtn.type = 'button';this.previousMonthBtn.classList = this.calendarControlsNavegateClasslist;this.previousMonthBtn.innerHTML = '<i class="fas fa-chevron-left px-1"></i>';
        this.previousMonthBtn.onclick = () => this.previousMonth();
        this.nextMonthBtn = document.createElement('button');this.nextMonthBtn.type = 'button';this.nextMonthBtn.classList = this.calendarControlsNavegateClasslist;this.nextMonthBtn.innerHTML = '<i class="fas fa-chevron-right px-1"></i>';
        this.nextMonthBtn.onclick = () => this.nextMonth();
        td2.appendChild(this.currentMonthBtn);
        td2.appendChild(this.previousMonthBtn);
        td2.appendChild(this.nextMonthBtn);
        row.appendChild(td1);
        row.appendChild(td2);
        caption.appendChild(row);
        this.calendar.appendChild(caption);
        // --------------
        this.thead = document.createElement('thead');
        let headers = document.createElement('tr');
        headers.innerHTML = `<td class="${this.headerClasslist}">DOM</td><td class="${this.headerClasslist}">SEG</td><td class="${this.headerClasslist}">TER</td><td class="${this.headerClasslist}">QUA</td><td class="${this.headerClasslist}">QUI</td><td class="${this.headerClasslist}">SEX</td><td class="${this.headerClasslist}">SAB</td>`;
        this.thead.appendChild(headers);
        this.tbody = document.createElement('tbody');
        this.calendar.appendChild(this.thead);
        this.calendar.appendChild(this.tbody);
        // Contruindo a div de tasks
        this.taskContainer = document.createElement('div');this.taskContainer.classList = this.taskContainerClassList;
        this.taskList = document.createElement('ul');this.taskList.classList = this.taskListClasslist;
        this.taskContainer.appendChild(this.taskList);
        this.container.appendChild(this.calendar);
        this.container.appendChild(this.taskContainer);
        if(this.view == 'calendar'){this.taskContainer.classList.add('d-none');}
        else{this.thead.classList.add('d-none');}
    }
    calendarRebuild(){
        this.monthName.innerHTML = `${this.monthNames[this.month - 1]} ${this.year}`;
        if(this.view == 'tasks'){this.tasksRebuild();this.summary = {};return false;}
        let daysCount = 1;
        let ajust = 0;
        this.summary.uteis = 0;this.summary.sabados = 0;this.summary.domingos = 0;this.summary.feriados = 0;
        this.startAt = new Date(`${this.year}-${this.month}-1 00:00`).getDay(); // Retorna de 0-6 (dom=0, seg=1,...)
        this.totalDays = new Date(this.year, this.month, 0).getDate(); // Retorna quantidade de dias do mes
        this.tbody.innerHTML = ''; // Limpa o tbody
        while(daysCount <= this.totalDays){
            let row = document.createElement('tr');
            if(daysCount == 1){ // Bloco executado somente no inicio da construcao, para preencher dias vazios
                for(let j = 0; j < this.startAt;j++){row.appendChild(this.__getTargetDay());}
                ajust = this.startAt;
            }
            for(let i = 0; i < 7 - ajust;i++){
                row.appendChild(this.__getTargetDay(daysCount));
                daysCount++;
            }
            this.tbody.appendChild(row);
            ajust = 0;
        }
        if(this.showSummary){this.buildSummary();}
        if(this.selectedDays.length > 0){this.selectDays(this.selectedDays, true)};
    }
    tasksRebuild(){
        if(this.view != 'tasks'){return false;}
        let count = 0;
        this.taskList.innerHTML = '';
        for(let item in this.events){
            if(item.includes(`${this.year}-${'0'+this.month+''.slice(-2)}`)){
                count++;
                let option = document.createElement('li');
                option.innerHTML = `<b>${item.slice(-2)}</b> - ${this.events[item]}`;
                this.taskList.appendChild(option);
            }
        }
        if(count == 0){
            let option = document.createElement('li');
            option.innerHTML = 'Nenhum evento registrado.';
            this.taskList.appendChild(option);
        }
    }
    buildSummary(){
        if(this.summaryEl == null){ // Caso container do summary ainda nao exista, cria elemento abaixo do calendario
            this.summaryEl = document.createElement('div');
            this.calendar.after(this.summaryEl);
            this.detail = document.createElement('div');this.detail.classList = 'pt-1';
            this.summaryEl.after(this.detail);
        }
        let curDate = new Date(`${this.year}-${this.month}-1`);
        this.detail.innerHTML = '';
        for(let i = 0;i < this.totalDays;i++){ 
            if(this.holidays.hasOwnProperty(`${this.year}-${('0'+this.month).slice(-2)}-${('0'+ (i + 1)).slice(-2)}`)){ // Aqui deve ser tratado no caso dos feriados
                this.summary['feriados']++;
                this.detail.innerHTML += `<b>${('0'+ (i + 1)).slice(-2)}</b> - ${this.holidays[`${this.year}-${('0'+this.month).slice(-2)}-${('0'+ (i + 1)).slice(-2)}`]}<br />`;
            }
            else if(curDate.getDay() == 0){this.summary['domingos']++;}
            else if(curDate.getDay() == 6){this.summary['sabados']++;}
            else{this.summary['uteis']++;}
            curDate.setDate(curDate.getDate() + 1); // Incrementa data
        }
        this.summaryEl.innerHTML = `<label class="badge opacity-75 fs-9 me-1 bg-success">UTIL: ${this.summary.uteis}</label>`;
        this.summaryEl.innerHTML += `<label class="badge opacity-75 fs-9 me-1 bg-primary">SAB: ${this.summary.sabados}</label>`;
        this.summaryEl.innerHTML += `<label class="badge opacity-75 fs-9 me-1 bg-orange">DOM: ${this.summary.domingos}</label>`;
        this.summaryEl.innerHTML += `<label class="badge opacity-75 fs-9 bg-dark">FER: ${this.summary.feriados}</label>`;
        
    }
    __getTargetDay(day=''){
        let td = document.createElement('td');
        let dateFormated = `${this.year}-${('0'+this.month).slice(-2)}-${('0'+day).slice(-2)}`; // Armazena a data formatada 'yyyy-mm-dd'
        if(day <= this.totalDays && day != ''){ // Caso seja data valida....
            if(this.holidays.hasOwnProperty(dateFormated)){ // Se data for um feriado, formata conforme especificado em this.holidayClasslist
                td.classList = this.holidayClasslist;
                td.title = this.holidays[dateFormated]; // Adiciona no title do elemento a descricao do feriado
            }
            else if(this.events.hasOwnProperty(dateFormated)){ // Se existir evento para data, formata conforme especificado em this.busyDayClasslist
                td.classList = this.busyDayClasslist;
                td.title = this.events[dateFormated]; // Adiciona no title do elemento a descricao do evento
            }
            else{td.classList = this.customDayClasslist;} // Caso contrario usa formado padrao
            td.innerHTML = day;
            td.dataset.date = dateFormated; // Adiciona data-attr 'date' usado no evento click do calendario
            if(this.onclick || this.canSelectDay){
                td.style.cursor = 'pointer';
                td.onclick = () => {
                    if(this.onclick){this.onclick(dateFormated);} // Aciona funcao fornecida ao instanciar objeto (caso exista)
                    if(this.canSelectDay){ //Implementa funcao para selecao de dia(s) no calendario
                        if(td.dataset.selected != 'true'){
                            if(!this.multiSelect && this.selectedDays.length > 0){ // Se nao permitido multi selecao desmarca dia marcado
                                let target = this.tbody.querySelector('[data-selected=true]');
                                let index = this.selectedDays.indexOf(dateFormated); // Localiza o indice da data no array
                                if(target){ // Se selecao anterior estiver sendo exibido (mesmo mes), altera a formatacao e remove do array
                                    target.classList = target.dataset.ocl;
                                    target.removeAttribute('data-selected');
                                }
                                this.selectedDays.splice(index,1); // Remove a data do array
                            }
                            this.selectedDays.push(dateFormated);
                            td.setAttribute('data-ocl', td.classList); // Armazena o classlist original caso desmarcado dia
                            td.classList = this.selectDayClasslist;
                            td.setAttribute('data-selected','true');
                        }
                        else{
                            let index = this.selectedDays.indexOf(dateFormated); // Localiza a data no array
                            this.selectedDays.splice(index,1); // Remove a data do array
                            td.classList = td.dataset.ocl;
                            td.removeAttribute('data-selected');
                        }
                    }
                    
                };
            }
        }
        else{td.classList = this.emptyDayClasslist;}
        return td;
    }
    currentMonth(){
        this.month = this.today.getMonth() + 1;
        this.year = this.today.getFullYear();
        if(this.onchange){this.onchange('currentMonth')}
        else{this.calendarRebuild()}
    }
    previousMonth(){
        if(this.month == 1){this.month = 12;this.year--;}
        else{this.month--;}
        if(this.onchange){this.onchange('previousMonth')}
        else{this.calendarRebuild()}
    }
    nextMonth(){
        if(this.month == 12){this.month = 1;this.year++;}
        else{this.month++;}
        if(this.onchange){this.onchange('nextMonth')}
        else{this.calendarRebuild()}
    }
    clearSelectedDays(){
        this.tbody.querySelectorAll('[data-selected=true]').forEach(e => {
            e.classList = e.dataset.ocl;
            e.removeAttribute('data-selected');
        });
        this.selectedDays = [];
    }
    goTo(year, month){ // Altera vizualizacao para ano e mes informados
        this.year = year;
        if(month > 0 && month < 13){this.month = month;}
        if(this.onchange){this.onchange('goTo')}
        else{this.calendarRebuild()}
    }
    changeView(){
        if(this.view == 'calendar'){
            this.view = 'tasks';
            if(this.canChangeView){this.changeViewBtn.innerHTML = '<i class="fas fa-calendar-alt"></i>'}
            this.taskContainer.classList.remove('d-none');
            this.thead.classList.add('d-none');
            this.tbody.classList.add('d-none');
            if(this.showSummary){this.detail.innerHTML = '';}
            if(this.summaryEl){this.summaryEl.classList.add('d-none');}
        }
        else{
            this.view = 'calendar';
            if(this.canChangeView){this.changeViewBtn.innerHTML = '<i class="fas fa-list-ul"></i>';}
            this.thead.classList.remove('d-none');
            this.tbody.classList.remove('d-none');
            if(this.summaryEl){this.summaryEl.classList.remove('d-none');}
            this.taskContainer.classList.add('d-none');
        }
        this.calendarRebuild();
    }
    selectDays(datas=[], printOnly=false){
        for(let i = 0;i < datas.length;i++){
            let target = this.tbody.querySelector(`[data-date='${datas[i]}']`);
            if(target){
                target.dataset.ocl = target.classList;
                target.classList = this.selectDayClasslist;
                target.dataset.selected = 'true';
                if(!printOnly){this.selectedDays.push(datas[i]);}
            }
        }
    }
}