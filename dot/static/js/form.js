/*
* Retorna ou atualiza elemento com a 'data atual' podendo ser acrescido dias, meses ou anos
*
* @version  1.1
* @since    19/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @param    {Int} dias Dias a serem acrecidos
* @param    {Int} meses Meses a serem acrecidos
* @param    {Int} anos Anos a serem acrecidos
* @param    {Bool} native Se true retorna data no formato americano (yyyy-mm-dd), se nao retorna formatado para PT-BR (dd/mm/aaaa)
* @param    {Element} el Elemento html que ira receber o valor, se omitido retorna a data na chamada da funcao
* @returns  {String} Retorna Data formatada caso nao definido elemento na chamada da funcao
* @example  
*    today();                 Retorna data atual (dd/mm/yyyy)
*    today(5);                Retorna data atual somando 5 dias
*    today(0,0,0,true);       Retorna data atual no formato native (yyyy-mm-dd)
*    today(0,0,0,false, el);  Insere a data atual no atributo value (ou innerHTML) do elemento informando
*/
function today(dias=0, meses=0, anos=0, native=false, el=null){
  var today = new Date();
  today.setDate(today.getDate() + dias);
  today.setMonth(today.getMonth() + meses + 1);
  today.setFullYear(today.getFullYear() + anos);
  const dd = String(today.getDate()).padStart(2, '0');
  const mm = String(today.getMonth()).padStart(2, '0');
  const yyyy = today.getFullYear();
  if(!el){return native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
  else{
    if(el.hasAttribute('value')){el.value = native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
    else{el.innerHTML = native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
  }}

/*
* Retorna ou atualiza elemento com a 'hora atual' podendo ser acrescido hora ou minutos
*
* @version  1.0
* @since    13/06/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @param    {Int} horas Horas a serem acrecidos
* @param    {Int} minutos Minutos a serem acrecidos
* @param    {Bool} segundos Setar true para mostrar segundos (default false)
* @param    {Element} el Elemento html que ira receber o valor, se omitido retorna a hora na chamada da funcao
* @returns  {String} Retorna Hora formatada caso nao definido elemento na chamada da funcao
* @example  
*    now();           Retorna hora atual (hh:mm)
*    now(5);          Retorna hora atual somando 5 horas
*    now(0,0,0, el);  Insere a hora atual no atributo value (ou innerHTML) do elemento informando
*/
function now(horas=0, minutos=0, segundos=false, el=null){
  var today = new Date();
  today.setHours(today.getHours() + horas);
  today.setMinutes(today.getMinutes() + minutos);
  const hh = String(today.getHours()).padStart(2, '0');
  const ii = String(today.getMinutes()).padStart(2, '0');
  const ss = String(today.getSeconds()).padStart(2, '0');
  if(!el){return segundos == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
  else{
    if(el.hasAttribute('value')){el.value = segundos == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
    else{el.innerHTML = segundos == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
  }}
