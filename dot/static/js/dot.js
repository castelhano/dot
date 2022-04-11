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
* Tooltip initializer
*
* @version  1.0
* @since    10/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Ao carregar a pagina, chame a funcao tooltipActivate()
* @example  tooltipActivate(); <span data-bs-toggle="tooltip" data-bs-placement="top" title="Meu foo">FOO</span>
*/
function tooltipActivate(){var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {return new bootstrap.Tooltip(tooltipTriggerEl)})}