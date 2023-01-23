/*
* FUNCAO LISTENER PARA EVENTOS DE TECLADO (keydown) DIVIDIDO EM 3 ETAPAS, PASSANDO PARA A PROXIMA ETAPA SOMENTE SE CORRESPONDENTE NAO LOCALIZADO 
* --
* @version 2.1
* @since   02/03/2022
* @author  Rafael Gustavo Alves {@email castelhano.rafael@gmail.com}
* @desc    1a ETAPA: LISTENER DE ATALHOS
* @param {dict} SHORTCUT_MAP DICIONARIO CONTENDO O MAPA DE TECLAS DE ATALHO, ONDE:
*   -> KEY DO DICT DEVE SER FORMADA PELA TECLA A SER ANALISADA (lowercase), SEGUIDO DE T (true) OU F (false) PARA OS COMBOS DE TECLA ALT, CTRL E SHIFT (NESTA ORDEM)
*   -> O VALOR DO DICIONARIO PODE SER O TRIGGER CLICK DE UM ELEMENTO (PARA ISSO INFORME # SEQUIDO DO ID DO OBJETO ALVO) OU
*   :: A CHAMADA DE UMA FUNCAO, PARA ISSO INICIE COM : SEGUIDO DO NOME DA FUNCAO A SER ACIONADA
* @example  SHORTCUT_MAP['xTFF'] = '#meubotao' EVENTO CLICK DO ELEMENTO ID: meubotao ACIONADO AO PRECIONAR ALT + X 
* @example  SHORTCUT_MAP['enterFTF'] = ':minhafuncao' CHAMA FUNCAO minhafuncao() AO PRECIONAR CTRL + ENTER
* -- 
* @desc    2a ETAPA: SIMULA TABULACAO AO PRECIONAR ENTER EM FORMULARIOS <form>, ONDE:
*   ->  FUNCAO IGNORA ELEMENTOS OCULTOS, DISABLED, OU COM tabindex MENOR QUE 0 (ZERO), BUSCANDO NESTES CASOS O PROXIMO ELEMENTO
* @param {boolean} TAB_ON_ENTER BOOLEANO QUE DEVE SER INSTANCIADO NA ORIGEM E SETADO PARA true PARA ATIVAR EVENTO DE TABULAR COM A TECLA ENTER:
* @example var TAB_ON_ENTER = true;
* -- 
* @desc    3a ETAPA: CHAMA FUNCAO eventHandler(e) QUE DEVE SER CRIADA E TRATADA NA ORIGEM CASO NAO LOCALIZE CORRESPONDENTE NAS ETAPAS ANTERIORES
*/
var SHORTCUT_MAP = {'vTFF':'#back','nTFF':'#add','lTFF':'#clear','gTFF':'#submit','/FTF':'#search','dTFF':'#download','iTFF':'#home','.TFF':'#app_root','mTFF':'#messages','sTFF':'#system','dFTF':'#docs'};

document.addEventListener('keydown', (e) => {
	// console.log(e);
	// 1) ETAPA
	let command = null;
	try {command = e.key.toLowerCase();command += e.altKey == true ? 'T': 'F';command += e.ctrlKey == true ? 'T': 'F';command += e.shiftKey == true ? 'T': 'F';}catch(err){command = '';}
	if(SHORTCUT_MAP[command]){
		if(SHORTCUT_MAP[command].charAt(0) == '#'){
			e.preventDefault();
			try {document.getElementById(SHORTCUT_MAP[command].substr(1,SHORTCUT_MAP[command].length)).click();} catch(err){}
		}else if(SHORTCUT_MAP[command].charAt(0) == ':'){e.preventDefault();window[SHORTCUT_MAP[command].substr(1,SHORTCUT_MAP[command].length)]();}
	}  
	// 2) ETAPA
	else if (e.key === 'Enter' && (typeof TAB_ON_ENTER !== 'undefined' && TAB_ON_ENTER == true) && (e.target.nodeName === 'INPUT' || e.target.nodeName === 'SELECT')) {
		e.preventDefault();
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
		// 3) ETAPA
		else{try{eventHandler(e);}catch(e){}}
	});