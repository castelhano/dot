function showDayTimeline(day){
    tbody.innerHTML = '';
    detail.innerHTML = '';
    let data = new Date(`${day} 00:00`);
    let [ano, mes, dia] = day.split('-');
    title.innerHTML = `${dia} ${calendar.monthNames[parseInt(mes) - 1]} <span class="text-purple">${translateWeekDay[data.getDay()]}</span> ${ano}`;
    if(calendar.holidays[day]){title.innerHTML += ` <b class="ms-1 text-danger help" title="${calendar.holidays[day]}">FERIADO</b>`;}
    // ***
    if(agendaMes[day]){
        for(key in agendaMes[day]){
            let record = agendaMes[day][key].fields;
            let tags = record.tags.split(';')
            let tagsEl = '';
            for(let tag in tags){tagsEl += `<span class="badge bg-purple me-1">${tags[tag]}</span>`}
            {% if perms.core.change_agenda %}
            let action = `<td class="text-end"><a class="btn btn-sm btn-dark py-0" href="/core_agenda_id/${agendaMes[day][key].pk}"><i class="fas fa-pen fs-8"></i></a></td>`
            {% else %}
            let action = '';
            {% endif %}
            tbody.innerHTML += `<tr class="pointer" onclick="showDetails(this,'${day}','${key}')"><td>${record?.inicio ? record.inicio.slice(0,5) : '--'} a ${record.termino ? record.termino.slice(0,5) : '--'}</td><td>${record.titulo}</td><td>${tagsEl}</td>${action}</tr>`;
        }
    }
    if(tbody.children.length == 0){
        tbody.innerHTML = '<tr><td colspan="4">Nenhum evento cadastrado</td></tr>';
    }
}


function showDetails(el, day, id){
    let [ano, mes, dia] = day.split('-');
    let dd = agendaMes[day][id].fields; // DayDetail
    let participantes = '';
    let anexoFileName = dd?.anexo ? dd.anexo.split('/')[6] : null;
    dd.participantes.forEach((e) => {participantes += `<span class="badge bg-dark me-1">${usuarios[e]}</span>`;});
    let create_at = new Date(dd.create_at);
    let create_at_f = `${create_at.getDate()}/${String(create_at.getMonth() + 1).padStart(2,'0')}/${create_at.getFullYear()}`
    detail.innerHTML = `<small>Criado em: <b>${create_at_f}</b> - <span class="text-primary text-capitalize">${dd.create_by}</span></small><hr class="m-0">`;
    detail.innerHTML += `<small>Local: <b>${dd.local || '--'}</b></small>`;
    detail.innerHTML += `<div class="mt-1">${dd.detalhe}</div>`;
    detail.innerHTML += `<div>${participantes}</div>`;
    detail.innerHTML += anexoFileName ? `<hr class="mt-2 mb-1">Anexo: <a href="/media/${dd.anexo}" target="_blank">${anexoFileName}</a>` : '';
    tbody.querySelectorAll('tr.table-secondary').forEach((e) => {e.classList.remove('table-secondary')});
    el.classList.add('table-secondary');
}


function getAgenda(options) {
    return new Promise(function(resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function() {
            agendaMes = {};
            calendar.events = {}
            let obj = JSON.parse(this.responseText);
            for(item in obj){
                calendar.events[obj[item].fields.data] = 'Eventos: Click para visualizar';
                if(agendaMes[obj[item].fields.data]){
                    agendaMes[obj[item].fields.data].push(obj[item]);
                }
                else{agendaMes[obj[item].fields.data] = [obj[item]]}
            }
            resolve(true);
        };
        xhr.onerror = reject;
        xhr.open("GET", `{% url 'core_get_agenda' %}?ano=${options.ano}&mes=${options.mes}`, true);
        xhr.send();
    });
}

function getFeriados(options) {
    return new Promise(function(resolve, reject) {
        var xhr = new XMLHttpRequest();
        xhr.onload = function() {
            calendar.holidays = JSON.parse(this.responseText);
            resolve(true);
        };
        xhr.onerror = reject;
        xhr.open("GET", `{% url 'core_get_feriados' %}?ano=${options.ano}`, true);
        xhr.send();
    });
}

function get_usuarios() { // Popula dicionario de usuarios (chamado uma unica vez ao carregar a pagina)
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200){
            if(this.responseText == ''){}
            else{
                let obj = JSON.parse(this.responseText);
                for(key in obj){usuarios[obj[key].pk] = obj[key].fields.username}
            }
        };
    }
    xhttp.open("GET", `{% url 'core_get_usuarios' %}`, true);
    xhttp.send();
}


