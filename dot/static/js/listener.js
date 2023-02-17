/*
* FUNCAO LISTENER PARA EVENTOS DE TECLADO (keydown) DIVIDIDO EM 3 ETAPAS, PASSANDO PARA A PROXIMA ETAPA SOMENTE SE CORRESPONDENTE NAO LOCALIZADO 
* --
* @version 3.0
* @since   02/03/2022
* @release 31/01/2023
* @author  Rafael Gustavo Alves {@email castelhano.rafael@gmail.com}
* @desc    1a ETAPA: LISTENER DE ATALHOS
* @param {dict} SHORTCUT_MAP DICIONARIO CONTENDO O MAPA DE TECLAS DE ATALHO, ONDE:
*   -> KEY DO DICT DEVE SER FORMADA PELA TECLA A SER ANALISADA (lowercase), SEGUIDO DE T (true) OU F (false) PARA OS COMBOS DE TECLA ALT, CTRL E SHIFT (NESTA ORDEM)
*   -> O VALOR DEVE SER UMA FUNCAO QUE SERA EXECUTADA AO ACIONAR TECLAS DEFINIDAS
* @example  SHORTCUT_MAP['xTFF'] = () => {meuBotao.click()}; ACIONA EVENTO CLICK DO ELEMENTO AO PRECIONAR ALT + X 
* @example  SHORTCUT_MAP['enterFTF'] = minhaFuncao; CHAMA FUNCAO minhafuncao() AO PRECIONAR CTRL + ENTER
* -- 
* @desc    2a ETAPA: SIMULA TABULACAO AO PRECIONAR ENTER EM FORMULARIOS <form>, ONDE:
*   ->  FUNCAO TRATA ELEMENTOS OCULTOS, DISABLED, OU COM tabindex MENOR QUE 0 (ZERO), BUSCANDO NESTES CASOS O PROXIMO ELEMENTO
* @param {boolean} TAB_ON_ENTER BOOLEANO QUE DEVE SER INSTANCIADO NA ORIGEM E SETADO PARA true PARA ATIVAR EVENTO DE TABULAR COM A TECLA ENTER:
* @example var TAB_ON_ENTER = true;
*/
var SHORTCUT_MAP = {
	'vTFF':() => {try{document.getElementById('back').click()}catch(e){}},
	'nTFF':() => {try{document.getElementById('add').click()}catch(e){}},
	'lTFF':() => {try{document.getElementById('clear').click()}catch(e){}},
	'gTFF':() => {try{document.getElementById('submit').click()}catch(e){}},
	'/FTF':() => {try{document.getElementById('search').click()}catch(e){}},
	'dTFF':() => {try{document.getElementById('jsTableDownloadCSV').click()}catch(e){}},
	'iTFF':() => {try{document.getElementById('home').click()}catch(e){}},
	'.TFF':() => {try{document.getElementById('app_root').click()}catch(e){}},
	'mTFF':() => {try{document.getElementById('offCanvasLink').click()}catch(e){}},
	'sTFF':() => {try{document.getElementById('system').click()}catch(e){}},
	'f1TFF':() => {try{document.getElementById('docs').click()}catch(e){}},
	'kTFF':() => {try{document.getElementById('shortcut_link_list').click()}catch(e){}},
	'qTFF':() => {try{document.getElementById('logout_link').click()}catch(e){}},
};

document.addEventListener('keydown', (e) => {
	// console.log(e);
	// 1) ETAPA
	let command = null;
	try {command = e.key.toLowerCase();command += e.altKey == true ? 'T': 'F';command += e.ctrlKey == true ? 'T': 'F';command += e.shiftKey == true ? 'T': 'F';}catch(err){command = '';}
	if(SHORTCUT_MAP[command]){
		if(command.slice(-3) != 'FFF'){e.preventDefault();} // Caso atalho seja sem combo (alt, ctrl, shift), nao previne comportamento default
		SHORTCUT_MAP[command](e);
	}  
	// 2) ETAPA
	else if (e.key === 'Enter' && (typeof TAB_ON_ENTER !== 'undefined' && TAB_ON_ENTER == true) && (e.target.nodeName === 'INPUT' || e.target.nodeName === 'SELECT')) {
		e.preventDefault();
		if(e.target.getAttribute('listener-js') == 'escape-tab'){return false;}
		try{
			var form = e.target.form;
			var index = Array.prototype.indexOf.call(form, e.target);
			if(form.elements[index + 1].disabled == false && form.elements[index + 1].offsetParent != null && form.elements[index + 1].tabIndex >= 0){form.elements[index + 1].focus();}
			else{
				let el = e.target.form.elements;
				let i = index + 1;
				let escape = false;
				while(i <= el.length && !escape){
					if(form.elements[i].disabled == false && form.elements[i].offsetParent != null && form.elements[i].tabIndex >= 0){form.elements[i].focus();escape = true;}
					else{i++;}
				}
			}
		}catch(e){}}
	});