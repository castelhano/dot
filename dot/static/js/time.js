/*
* BIBLIOTECA COM FUNCOES COMUNS PARA OPERACAO COM HORAS
*/

/*
* time_now | Retorna a hora atual em formato nativo ou localizado
*
* @version  1.0
* @since    19/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {Bool} seconds Informa se sera informado os segundos no retorno da funcao (default=false)
* @param    {Element} el Elemento html que ira receber o valor, se omitido retorna a hora na chamada da funcao
* @returns  {String} Retorna hora formatada caso nao definido elemento na chamada da funcao
* @example  time_now() || time_now(element) || time_now(null, true)
*/
function time_now(el=null,seconds=false){
  let today = new Date();
  const hh = String(today.getHours()).padStart(2, '0');
  const ii = String(today.getMinutes()).padStart(2, '0');
  const ss = String(today.getSeconds()).padStart(2, '0');
  if(!el){return seconds == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
  else{
    if(el.hasAttribute('value')){el.value = seconds == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
    else{el.innerHTML = seconds == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
  }
}

/*
* time_sum | Soma (ou subtrai) horas, minutos e/ou segundos a partir de uma hora informada
*
* @version  1.0
* @since    19/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} initial Hora inicial
* @param    {Int} h, m, s Horas, minutos e segundos a serem acrescidos / subtraidos
* @param    {Bool} seconds Booleano que informa se deve ser mostrado segundos no retorno (default=false)
* @param    {Element} el Elemento html que ira receber o valor, se omitido retorna a hora na chamada da funcao
* @returns  {String} Retorna hora formatada caso nao definido elemento na chamada da funcao
* @example  time_sum('04:25',0,10) || time_sum('04:25',-4) || time_sum('04:25',0,120,0,true) || time_sum('04:25',5,0,0,true, element)
*/
function time_sum(initial, h=0,m=0,s=0,seconds=false,el=null){
  let hh = parseInt(initial.split(':')[0]) + h;
  let ii = parseInt(initial.split(':')[1]) + m;
  let ss = initial.split(':')[2] ? parseInt(initial.split(':')[2]) + s : s;
  while(ss > 59){ss -= 60; ii++;}
  while(ii > 59){ii -= 60; hh++;}
  while(ss < 0){ss += 60; ii--;}
  while(ii < 0){ii += 60; hh--;}
  if(!el){return seconds == true ? `${String(hh).padStart(2, '0')}:${String(ii).padStart(2, '0')}:${String(ss).padStart(2, '0')}` : `${String(hh).padStart(2, '0')}:${String(ii).padStart(2, '0')}`;}
  else{
    if(el.hasAttribute('value')){el.value = seconds == true ? `${String(hh).padStart(2, '0')}:${String(ii).padStart(2, '0')}:${String(ss).padStart(2, '0')}` : `${String(hh).padStart(2, '0')}:${String(ii).padStart(2, '0')}`;}
    else{el.innerHTML = seconds == true ? `${String(hh).padStart(2, '0')}:${String(ii).padStart(2, '0')}:${String(ss).padStart(2, '0')}` : `${String(hh).padStart(2, '0')}:${String(ii).padStart(2, '0')}`;}
  }
}

/*
* time_delta | Retorna em minutos a diferenca entre duas horas
* !! Se a hora2 for menor que a hora1, considera que virou o dia e soma 24 horas na hora2 
*
* @version  1.0
* @since    19/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} init Hora inicial (subtraendo)
* @param    {String} end Hora final (minuendo)
* @returns  {Int} Minutos entre as duas horas
* @example  time_delta('04:25', '05:32')
*/
function time_delta(init, end){
  let minuendo = end.split(':').map(function(x){return parseInt(x)});
  if(!minuendo[3]){minuendo.push(0)}
  let subtraendo = init.split(':').map(function(x){return parseInt(x)});
  if(!subtraendo[3]){subtraendo.push(0)}
  let hh = minuendo[0] > subtraendo[0] ? minuendo[0] - subtraendo[0] : (minuendo[0] + 24) - subtraendo[0];
  let ii = minuendo[1] - subtraendo[1];
  let ss = minuendo[2] - subtraendo[2];
  return (hh * 60) +  (ii) + (ss / 60);
}

/*
* time_compare | Compara duas horas e retorna se sao iguais, ou se h1 > h2 ou h1 < h2
*
* @version  1.0
* @since    19/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} h1, h2 Horas para comparação
* @returns  {Int} 1 se h1 > h2 || 0 se h1 == h2  || -1 se h1 < h2
* @example  time_compare('04:25', '04:32')
*/
function time_compare(h1, h2){
  let h1_list = h1.split(':').map(function(x){return parseInt(x)});
  if(!h1_list[3]){h1_list.push(0)}
  let h2_list = h2.split(':').map(function(x){return parseInt(x)});
  if(!h2_list[3]){h2_list.push(0)}
  let h1_size = (h1_list[0] * 60) + (h1_list[1]) + (h1_list[2] / 60);
  let h2_size = (h2_list[0] * 60) + (h2_list[1]) + (h2_list[2] / 60);
  return h1_size > h2_size ? 1 : h1_size < h2_size ? -1 : 0;
}

/*
* time_stamp | Retorna data atual em milisegundos podendo receber um prefixo e/ou posfixo
*
* @version  1.0
* @since    18/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} prefix String que sera adicionada antes da hora atual em milisegundos
* @param    {String} posfix String que sera adicionada apos a hora atual em milisegundos
* @returns  {String} String formatada
* @example  time_stamp() || time_stamp('ID_') || time_stamp('ID_', ';')
*/
function time_stamp(prefix='', posfix=''){
  let now = new Date();
  return `${prefix}${now.toISOString()}${posfix}`;
}