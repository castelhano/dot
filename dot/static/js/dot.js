const __sw = screen.width;
const __ss = __sw >= 1400 ? 'xxl' : __sw >= 1200 ? 'xl' : __sw >= 992 ? 'lg' : __sw >= 768 ? 'md' : 'sm' ;

/*
* dotAlert Gera um alerta (bootstrap alert)
*
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} tipo Tipo do alerta (info, danger, warning, success, primary, etc..)
* @param    {String} mensagem Mensagem do alerta
* @example  dotAlert('warning', 'Este eh um <b>alerta de exemplo</b>')
*/
function dotAlert(tipo, mensagem){
  try {document.querySelector('[data-type="dotAlert"]').remove();}catch(e){}let e = document.createElement('div');e.setAttribute('data-type','dotAlert');e.style.zIndex = 100;let b = document.createElement('button');b.classList.add('btn-close');b.setAttribute('data-bs-dismiss','alert');e.classList.add('alert', `alert-${tipo}`,'alert-dismissible','fade','show','mb-1');e.innerHTML = mensagem;e.appendChild(b);document.body.appendChild(e);setTimeout(function() {e.remove()}, 4500);}

/*
* getCookie Busca no arquivo de cookie pela chave informada e retorna o valor
*
* @version  1.0
* @since    31/08/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} name
* @returns  {String} Valor da chave (se encontrada) ou null caso nao encontrado
* @example  let token = getCookie('csrftoken');
*/
function getCookie(name) {let cookieValue = null;if (document.cookie && document.cookie !== ''){const cookies = document.cookie.split(';');for(let i = 0; i < cookies.length; i++){const cookie = cookies[i].trim();if (cookie.substring(0, name.length + 1) === (name + '=')){cookieValue = decodeURIComponent(cookie.substring(name.length + 1));break;}}}return cookieValue;}


/*
* dotAppData Busca (ajax) no diretorio app_data, objeto json informando o path relativo
*
* @version  1.0
* @since    26/08/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} path Caminho relativo Ex.: 'core/usuarios.json'
* @returns  {Object} Retorna objeto json com dados solicitados
* @example  var data = [];
*           dotAppData('{% url 'app_data' 'data_test.json' %}').then((r) => data = r);
*           dotAppData('{% url 'app_data' 'data_test.json' %}').then((r) => data = r).catch(() = > {...});
*/
function dotAppData(url) {return new Promise(function(resolve, reject) {var xhr = new XMLHttpRequest();xhr.onload = function() {let d = JSON.parse(this.responseText);if(typeof d != 'object'){d = JSON.parse(d)}resolve(d);};xhr.onerror = reject;xhr.open('GET', url);xhr.send();});}

/*
* Tooltip initializer
*
* @version  1.0
* @since    10/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Ao carregar a pagina, chame a funcao tooltipActivate()
* @example  tooltipActivate(); <span data-bs-toggle="tooltip" data-bs-placement="top" title="Meu foo">FOO</span>
*/
function tooltipActivate(){var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {return new bootstrap.Tooltip(tooltipTriggerEl)})}

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

/*
* prismStart
*
* @version  1.0
* @since    12/07/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Adiciona botão para copiar para clipboard conteudo dentro das tags pre > code
* @depend   [prism.js, prism.css] (dependecia apenas de estilo)
* @example  <pre><code class="language-javascript">foo += 5;</code></pre>
*           prismStart();
*/
function prismStart(){
  document.querySelectorAll('pre').forEach((pre) => {
    if(navigator.clipboard && __ss != 'sm'){
      let container = document.createElement('div');container.style.position = 'relative';container.style.height = '1px';container.style.zIndex = '1000';
      let btn = document.createElement('span');
      btn.title = 'Copiar';
      btn.classList.add('code-btn-copy');
      btn.innerHTML = '<i class="fas fa-copy"></i>';
      btn.addEventListener('click', code_copy_clipboard);
      container.appendChild(btn);
      pre.before(container);
    }
  });


  function code_copy_clipboard(e){
    let copyLabel = '<i class="fas fa-copy"></i>';
    let doneLabel = '<i class="fas fa-check"></i>';
    let b = e.target.tagName == 'SPAN' ? e.target : e.target.parentElement;
    let t = b.parentNode.nextSibling.innerText;
    navigator.clipboard.writeText(t);
    b.innerHTML = doneLabel;
    setTimeout(()=>{b.innerHTML = copyLabel;}, 2000)
  }
}

// ******************************************************************************
// ONLOAD EVENTS                                                                *
// Todo o codigo abaixo sera executado antes do fechamento do </body>           *
// ******************************************************************************
// ALTERA TAB INDEX DE SELECTS COM A CLASS readonly
const readonly_els = document.querySelectorAll('select.readonly');for(let i = 0; i < readonly_els.length; i++){readonly_els[i].tabIndex = -1;}
