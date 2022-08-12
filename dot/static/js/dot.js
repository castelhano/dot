const __sw = screen.width;
const __ss = __sw >= 1400 ? 'xxl' : __sw >= 1200 ? 'xl' : __sw >= 992 ? 'lg' : __sw >= 768 ? 'md' : 'sm' ;

/*
* Alerta de sistema
*
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} tipo Tipo do alerta (info, danger, warning, success, primary, etc..)
* @param    {String} mensagem Mensagem do alerta
* @example  dotAlert('warning', 'Este eh um <b>alerta de exemplo</b>')
* TODO:     adicionar data-attr para antes de gerar novo alerta excluir se ja existir algum
*/
function dotAlert(tipo, mensagem){let e = document.createElement('div');let b = document.createElement('button');b.classList.add('btn-close');b.setAttribute('data-bs-dismiss','alert');e.classList.add('alert', `alert-${tipo}`,'alert-dismissible','fade','show','mb-1');e.innerHTML = mensagem;e.appendChild(b);document.body.appendChild(e);}

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
  document.querySelectorAll('pre').forEach(pre => {
    if(navigator.clipboard && __ss != 'sm'){
      let copyLabel = '<i class="fas fa-copy"></i>';
      let btn = document.createElement('span');
      btn.title = 'Copiar';
      btn.classList.add('code-btn-copy');
      btn.innerHTML = copyLabel;
      btn.addEventListener('click', code_copy_clipboard);
      pre.appendChild(btn);
    }
  });
  function code_copy_clipboard(e){
    let copyLabel = '<i class="fas fa-copy"></i>';
    let doneLabel = '<i class="fas fa-check"></i>';
    const b = e.srcElement.tagName == 'SPAN' ? e.srcElement : e.srcElement.parentElement;
    const t = b.parentElement.querySelector("code").innerText;
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