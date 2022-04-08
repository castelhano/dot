/*
* Alerta de sistema
*
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} tipo Tipo do alerta (info, danger, warning, success, primary, etc..)
* @param    {String} mensagem Mensagem do alerta
* @example  dotAlert('warning', 'Este eh um <b>alerta de exemplo</b>')
*/
function dotAlert(tipo, mensagem){let e = document.createElement('div');let b = document.createElement('button');b.classList.add('btn-close');b.setAttribute('data-bs-dismiss','alert');e.classList.add('alert', `alert-${tipo}`,'alert-dismissible','fade','show','mb-1');e.innerHTML = mensagem;e.appendChild(b);document.body.appendChild(e);}

/*
* Dot javascript interpolation
*
* @version  1.0
* @since    07/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Implementa interpolacao (simplificada) direto no document, buscando tag dotPlot
* @param    {Dict} map Dicionario com nome da variavel e valor para interpolar bo doc
* @example  var map={'foo':55,'fei':22}; dotPlotJs(map); ou dotPlotJs(map, '--');
* @see      {@link https://stackoverflow.com/questions/62382939/vanilla-htmljs-dynamic-interpolation}
*/
function jsPlot(map, if_null=''){
  [...document.querySelectorAll("dotPlot")].forEach(el => {
    if(map[el.getAttribute('data')] != undefined){el.innerText = map[el.getAttribute('data')];}
    else{el.innerText = if_null}
   })
}