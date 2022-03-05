/*
* Alerta de sistema
*
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} tipo Tipo do alerta (info, danger, warning, success, primary, etc..)
* @param    {String} mensagem Mensagem do alerta
* @example  dotAlert('warning', 'Este eh um <b>alerta de exemplo</b>')
*/
function dotAlert(tipo, mensagem){let e = document.createElement('div');let b = document.createElement('button');b.classList.add('btn-close');b.setAttribute('data-bs-dismiss','alert');e.classList.add('alert', `alert-${tipo}`,'alert-dismissible','fade','show','mb-1');e.innerHTML = mensagem;e.appendChild(b);document.body.appendChild(e);}