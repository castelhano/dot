const __sw = screen?.width || null;
const __ss = __sw == null ? null : __sw >= 1400 ? 'xxl' : __sw >= 1200 ? 'xl' : __sw >= 992 ? 'lg' : __sw >= 768 ? 'md' : 'sm' ;

/*
* dotAlert  Gera um alerta (bootstrap alert)
* dotNotify Gera um alerta simples, na caixa de norificação do systema
*
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} tipo Tipo do alerta (info, danger, warning, success, primary, etc..)
* @param    {String} mensagem Mensagem do alerta
* @param    {Bool} autodismiss [Opcional] Remove automaticamente alerta apos 4,5 segundos se setado para true (default), altere para false para exigir remocao manual
* @example  dotAlert('warning', 'Este eh um <b>alerta de exemplo</b>')
* @example  dotNotify('danger', 'Este eh um <b>alerta de exemplo</b>')
*/
function dotAlert(tipo, mensagem, autodismiss=true){
  try {document.querySelector('[data-type="dotAlert"]').remove();}catch(e){}let e = document.createElement('div');e.setAttribute('data-type','dotAlert');e.style.zIndex = 100;let b = document.createElement('button');b.classList.add('btn-close');b.setAttribute('data-bs-dismiss','alert');e.classList.add('alert','slideIn','dotAlert',`alert-${tipo}`,'alert-dismissible','fade','show','mb-0');e.innerHTML = mensagem;e.appendChild(b);document.body.appendChild(e);if(autodismiss){setTimeout(function() {e.remove()}, 5000);}}

function dotNotify(tipo, mensagem, autodismiss=true){
  let e = document.createElement('div'); e.classList = `alert alert-${tipo} alert-dismissible slideIn mb-2`; let b = document.createElement('button'); b.classList = 'btn-close'; b.setAttribute('data-bs-dismiss','alert'); e.innerHTML = mensagem; e.appendChild(b); document.getElementById('notify_container').appendChild(e); if(autodismiss){setTimeout(function() {e.remove()}, 4500);} }

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
* form2Dict Retorna dados do formulario como dict (object)
*
* @version  1.0
* @since    01/04/2023
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
* @param    {Element} Formulario alvo
* @returns  {Object}  Retorna dicionario com dados do form
* @example  let data = form2Dict(document.getElementById('my_form'));
*/
function form2Dict(form){let formData = new FormData(form);let resp = {};for([key, value] of formData){resp[key] = value}return resp;}

/*
* formLoad  Recebe dicionario e carrega dados no respectivo campo (caso exista)
*
* @version  1.0
* @since    01/04/2023
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
* @param    {Object} Dicionario com dados a serem carregados
* @param    {Array}  Lista com campos a serem ignorados. Ex: ['detalhe','sexo']
* @example  formLoad({nome:'Rafael', idade:'25'}); Busca os campos id_nome e id_idade e atribui respectivo valor
*/
function formLoad(dict, ignore=[]){for(key in dict){if(!ignore.includes(key)){try{document.getElementById(`id_${key}`).value = dict[key]}catch(e){}}}}


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
*           dotAppData('{% url 'app_data' 'ope-i18n-en.json' %}'); para subpastas use - ao invez de /
*/
function dotAppData(url) {return new Promise(function(resolve, reject) {let xhr = new XMLHttpRequest();xhr.onload = function() {let d = JSON.parse(this.responseText);if(typeof d != 'object'){d = JSON.parse(d)}resolve(d);};xhr.onerror = reject;xhr.open('GET', url);xhr.send();});}

/*
* dotAppDataUpdate Salva (ajax) no diretorio app_data, objeto json informando o path relativo
*
* @version  1.0
* @since    08/02/2023
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @example  dotAppDataUpdate({url: '/app_data/foo.json',data: JSON.stringify({...}),onSuccessMsg: 'Registro salvo com <b>success</b>'})
*/
function dotAppDataUpdate(options){let token = getCookie('csrftoken');let xhttp = new XMLHttpRequest();xhttp.onreadystatechange = function(){if(this.readyState == 4){if(this.status == 200){if(options?.showSuccessAlert == true || options?.showSuccessAlert == undefined){dotAlert(options?.onSuccessType || 'success', options?.onSuccessMsg || 'Registro salvo com <b>sucesso</b>')};if(options?.onSuccess){options.onSuccess()}}else{dotAlert(options?.onErrorType || 'danger', options?.onErrorMsg || '<b>Erro</b> ao salvar registro');if(options?.onError){options.onError()}}}};xhttp.open("POST", `${options.url}`, true);xhttp.setRequestHeader('X-CSRFToken', token);xhttp.send(options.data);}

/*
* Tooltip initializer
*
* @version  1.0
* @since    10/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Ao carregar a pagina, chame a funcao tooltipActivate()
* @example  tooltipActivate(); <span data-bs-toggle="tooltip" data-bs-placement="top" data-bs-html="true" title="Meu foo">FOO</span>
*/
function tooltipActivate(){let tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));let tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {return new bootstrap.Tooltip(tooltipTriggerEl)})}


function formDisable(form){
  let elements = form.elements;
  for(i in elements){
    if(elements[i] instanceof HTMLElement && elements[i].getAttribute('dot-role') == 'alwaysEnable'){continue;} // Para habilitar um controle num form disabled adicione o attr dot-role='always_enable'
    if(['INPUT','TEXTAREA','BUTTON'].includes(elements[i].tagName)){elements[i].disabled = true;}
    else if(elements[i].tagName == 'SELECT'){elements[i].classList.add('readonly');elements[i].tabIndex = -1;}
  }
}

function formReadonly(form){
  let elements = form.elements;
  for(i in elements){
    if(elements[i] instanceof HTMLElement && elements[i].getAttribute('dot-role') == 'alwaysEnable'){continue;} // Para habilitar um controle num form disabled adicione o attr dot-role='always_enable'
    if(['INPUT','TEXTAREA'].includes(elements[i].tagName)){elements[i].readonly = true; elements[i].onclick = ()=> {return false};}
    else if(elements[i].tagName == 'SELECT'){elements[i].classList.add('readonly');elements[i].tabIndex = -1;}
  }
}

/*
* Retorna ou atualiza elemento com a 'data atual' podendo ser acrescido dias, meses ou anos
*
* @version  1.1
* @since    19/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @param    {Int} days Dias a serem acrecidos
* @param    {Int} months Meses a serem acrecidos
* @param    {Int} yeras Anos a serem acrecidos
* @param    {Bool} native Se true retorna data no formato (yyyy-mm-dd), se nao retorna formatado para PT-BR (dd/mm/aaaa)
* @param    {Element} target Elemento html que ira receber o valor, se omitido retorna a data na chamada da funcao
* @returns  {String} Retorna Data formatada caso nao definido elemento na chamada da funcao
* @example  
*    dateToday();               Retorna data atual (dd/mm/yyyy)
*    dateToday({days:5});       Retorna data atual somando 5 dias
*    dateToday({native:true});  Retorna data atual no formato native (yyyy-mm-dd)
*    dateToday({target: el});   Insere a data atual no atributo value (ou innerHTML) do elemento informando
*/
function dateToday(opt={}){
  let today = new Date();
  if(opt.days){today.setDate(today.getDate() + opt.days)}
  if(opt.months){today.setMonth(today.getMonth() + opt.months)}
  if(opt.years){today.setFullYear(today.getFullYear() + opt.years)}
  const dd = String(today.getDate()).padStart(2, '0');
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const yyyy = today.getFullYear();
  if(!opt.target){return opt.native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
  else{
    if(opt.target.hasAttribute('value')){opt.target.value = opt.native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
    else{opt.target.innerHTML = opt.native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
  }}

/*
* Retorna ou atualiza elemento com a 'hora atual' podendo ser acrescido hora ou minutos
*
* @version  1.0
* @since    13/06/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com}
* @param    {Int} hours Horas a serem acrecidos
* @param    {Int} minutes Minutos a serem acrecidos
* @param    {Bool} showSeconds Setar true para mostrar segundos
* @param    {Element} target Elemento html que ira receber o valor, se omitido retorna a hora na chamada da funcao
* @returns  {String} Retorna Hora formatada caso nao definido elemento na chamada da funcao
* @example  
*    timeNow();           Retorna hora atual (hh:mm)
*    timeNow({hour:5});   Retorna hora atual somando 5 horas
*    timeNow({target:el, showSeconds:true}); Insere a hora atual no atributo value (ou innerHTML) do elemento informando no formato 'hh:mm:ss'
*/
function timeNow(opt={}){
  let today = new Date();
  if(opt.hours){today.setHours(today.getHours() + opt.hours)}
  if(opt.minutes){today.setMinutes(today.getMinutes() + opt.minutes)}
  const hh = String(today.getHours()).padStart(2, '0');
  const ii = String(today.getMinutes()).padStart(2, '0');
  const ss = String(today.getSeconds()).padStart(2, '0');
  if(!opt.target){return opt.showSeconds == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
  else{
    if(opt.target.hasAttribute('value')){opt.target.value = opt.showSeconds == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
    else{opt.target.innerHTML = opt.showSeconds == true ? `${hh}:${ii}:${ss}` : `${hh}:${ii}`;}
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

  function code_copy_clipboard(e){ // Funcao auxiliar ao componente prism
    let copyLabel = '<i class="fas fa-copy"></i>';
    let doneLabel = '<i class="fas fa-check"></i>';
    let b = e.target.tagName == 'SPAN' ? e.target : e.target.parentElement;
    let t = b.parentNode.nextSibling.innerText;
    navigator.clipboard.writeText(t);
    b.innerHTML = doneLabel;
    setTimeout(()=>{b.innerHTML = copyLabel;}, 2000)
  }
}

/*
* Funcao verifica se elemento nao esta visivel (retorna true para hidden e false para visivel)
*
* @version  1.0
* @since    05/02/2023
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
* @param    {Elm} Elemento html
* @example  isHidden(document.getElementById('id_cpf'))
*/
function isHidden(el){return (el.offsetParent === null)}

// ******************************************************************************
// ONLOAD EVENTS                                                                *
// Todo o codigo abaixo sera executado antes do fechamento do </body>           *
// ******************************************************************************
// ALTERA TAB INDEX DE SELECTS COM A CLASS readonly
document.querySelectorAll('select.readonly').forEach((e) => {e.tabIndex = -1});
