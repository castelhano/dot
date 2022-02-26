var patamares = [], frequencia = [], carros = [];

{% if planejamento.patamares == '' %}
{% for patamar in planejamento.linha.patamares %}
patamares.push([{{patamar.inicial}}, {{patamar.final}}, {{patamar.ida}}, {{patamar.volta}},0,0]);
{% endfor %}
{% else %}

let tbody = document.getElementById('patamares_tbody');
patamares = {{planejamento.patamares}};
for(i=0;i < patamares.length;i++){
  tbody.innerHTML += `<tr><td class="table-secondary">${patamares[i][0]}</td><td class="table-secondary">${patamares[i][1]}</td><td id="${i}_2" contenteditable="true" oninput="setPatamar(this.id, this.innerHTML)">${patamares[i][2]}</td><td id="${i}_3" contenteditable="true" oninput="setPatamar(this.id, this.innerHTML)">${patamares[i][3]}</td><td id="${i}_4" contenteditable="true" oninput="setPatamar(this.id, this.innerHTML)">${patamares[i][4]}</td><td id="${i}_5" class="table-warning text-truncate">${patamares[i][5]}</td></tr>`;
}
{% endif %}

function submitForm(){
  document.getElementById('id_patamares').value = JSON.stringify(patamares);
  return true;
}
function setPatamar(id, value){
  let x = id.split('_')[0], y = id.split('_')[1];
  patamares[x][y] = parseInt(value);
  patamares[x][5] = calculaFrequencia(patamares[x][2] + patamares[x][3], patamares[x][4]);
  document.getElementById(`${x}_5`).innerHTML = patamares[x][5]; //Ajusta valor da frequencia calculada
}
function calculaFrequencia(ciclo, frota){return frota > 0 ? parseFloat(ciclo / frota) : 0;}

function getFaixa(hora){return parseInt(hora.split(':')[0]) < 24 ? parseInt(hora.split(':')[0]) : parseInt(hora.split(':')[0]) - 24;}
function getPatamar(faixa){for(i=0;i < patamares.length;i++){if(faixa >= patamares[i][0] && faixa <= patamares[i][1]){return [patamares[i][2], patamares[i][3], patamares[i][2] + patamares[i][3], patamares[i][4], patamares[i][5]]}}}

function format2Digits(numero){return ("0" + numero).slice(-2)};

function horaAdd(hora, freq){try {let h = parseInt(hora.split(':')[0]), m = parseInt(hora.split(':')[1]) + parseInt(freq);while(m > 59){ m = m - 60; h++;}return `${format2Digits(h)}:${format2Digits(m)}`;} catch(e){console.log(e);}}
function horaSub(hora, freq){try {let h = parseInt(hora.split(':')[0]), m = parseInt(hora.split(':')[1]) - parseInt(freq);while(m < 0){ m = m + 60; h--;}return `${format2Digits(h)}:${format2Digits(m)}`;} catch(e){console.log(e);}}