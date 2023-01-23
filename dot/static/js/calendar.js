/*
* calendarJS Implementa compondente para calendario
*
* @version  1.0
* @since    23/01/2023
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
*/

class jsCalendar{
    constructor(options){
        this.today = new Date();
        this.year = options?.year || this.today.getFullYear();
        this.month = options?.month > 0 && options?.month < 13 ? options?.month : false || this.today.getMonth() + 1;
        this.startAt = new Date(`${this.year}-${this.month}-1`).getDay(); // Retorna de 0-6 (dom=0, seg=1,...)
        this.totalDays = new Date(this.year, this.month, 0).getDate();
        // --------------------------
        this.container = options?.container || document.body; // parentNode do calendario, caso nao informado append no body
        this.calendarClasslist = options?.calendarClasslist || 'table border text-center'; // classlist do calendar
        this.headerClasslist = options?.headerClasslist || 'border'; // classlist do cabecalho
        this.customDayClasslist = options?.customDayClasslist || 'border py-3 bg-light fs-5'; // classlist do calendar

        this.events = []; // Armazena json com os eventos/feriados 
        // --------------------------
        this.createCalendar();
    }
    createCalendar(){
        let calendar = document.createElement('table');
        calendar.classList = this.calendarClasslist;

        let headers = document.createElement('tr');
        headers.classList = this.headersClasslist;
        headers.innerHTML = `<td class="${this.headerClasslist}">DOM</td><td class="${this.headerClasslist}">SEG</td><td class="${this.headerClasslist}">TER</td><td class="${this.headerClasslist}">QUA</td><td class="${this.headerClasslist}">QUI</td><td class="${this.headerClasslist}">SEX</td><td class="${this.headerClasslist}">SAB</td>`;
        let row = document.createElement('tr');
        row.appendChild(this.getTargetDay(1));
        row.appendChild(this.getTargetDay(2));
        row.appendChild(this.getTargetDay(3));
        row.appendChild(this.getTargetDay(4));
        row.appendChild(this.getTargetDay(5));
        row.appendChild(this.getTargetDay(6));
        row.appendChild(this.getTargetDay(7));
        calendar.appendChild(headers);
        calendar.appendChild(row);
        this.container.appendChild(calendar);
    }
    getTargetDay(data){
        let day = document.createElement('td');
        day.classList = this.customDayClasslist;
        day.innerHTML = data;
        return day;
    }
}