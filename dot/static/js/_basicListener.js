/* BASIC LISTENER
** RAFAEL GUSTAVO 
** VERSÃO 2.1
** LISTENER DIVIDIDO EM 04 ETAPAS, PASSANDO PARA A PROXIMA ETAPA SOMENTE SE ATALHO CORRESPONDENTE NAO LOCALIZADO
** 1) ACIONA TRIGGER CLICK BASEADO NO ID DO ELEMENTO PARA ATALHOS PREDEFINIDOS (ADD, SAVE, CLEAR, BACK, SEARCH, DOWNLOAD, etc)
**    * BASTA SETAR O ID DO ELEMENTO (button, a, etc) PARA id='add' PARA JA RESPONDER PELO ATALHO ALT+N
** 2) VERIFICA POR EVENTO DE TECLA ENTER EM CAMPO DE FORMULARIO PARA SIMULAR TABULACAO AO PRECIONAR ENTER
**    * ELEMENTO PRECISA FAZER PARTE DE UM FORMULARIO (INSERIDO NUM ELEMENTO <form>)
**    * DEVE SER PREVIAMENTE INSTANCIADO NA PAGINA DE ORIGEM A VARIAVEL TAB_ON_ENTER E SETADO PARA true
**    * LOGICA CONSISTE CAMPOS BLOQUEADOS, OCULTOS OU COM tabIndex MENORES QUE ZERO, BUSCANDO PROXIMO ELEMENTO DISPONIVEL
**    !! NAO LEVA EM CONSIDERACAO ORDEM DE TABULACAO MANUAL, USA TABULACAO POR ORDEM DE INSERCAO DOS ELEMENTOS
** 3) BUSCA ATALHO NO DICIONARIO SHORTCUT_MAP QUE DEVE SER INSTANCIADO NA PAGINA DE ORIGEM
**    * KEY DO DICT DEVE SER FORMADA PELA TECLA A SER ANALISADA, SEGUIDO DE T (true) OU F (false) PARA OS COMBOS DE TECLA ALT, CTRL E SHIFT (NESTA ORDEM), EX:
**    * eTFF TRIGGER PARA TECLA E JUNTAMENTE COM O ALT (USE A KEY SEMPRE EM CAIXA BAIXA)
**    * O VALOR DO DICIONARIO PODE SER O TRIGGER CLICK DE UM ELEMENTO (PARA ISSO INFORME # SEQUIDO DO ID DO OBJETO ALVO) EX #meu_botao OU
**    * A CHAMADA DE UMA FUNCAO, PARA ISSO INICIE COM : SEGUIDO DO NOME DA FUNCAO A SER ACIONADA EX :minha_funcao (NAO PRECISA DE PARENTESE E NAO ACEITA PARAMETROS)
** 4) SE NENHUMA CORRESPONDENCIA, CHAMA FUNÇÃO eventHandler() QUE DEVE SER IMPLEMENTADA NA ORIGEM
**/

document.addEventListener('keydown', (e) => {
	// console.log(e);
  // 1) ETAPA
  if ((e.altKey) && (e.key.toLowerCase() === 'v')) {e.preventDefault();try{document.getElementById('back').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 'n')) {e.preventDefault();try{document.getElementById('add').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 'l')) {e.preventDefault();try{document.getElementById('clear').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 'g')) {e.preventDefault();try{document.getElementById('submit').click();}catch(e){}}
  else if ((e.ctrlKey) && (e.key === '/')) {e.preventDefault();try{document.getElementById('search').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 'd')) {e.preventDefault();try{document.getElementById('download').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 'i')) {e.preventDefault();try{document.getElementById('home').click();}catch(e){}}
  else if ((e.altKey) && (e.key === '.')) {e.preventDefault();try{document.getElementById('app_root').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 'm')) {e.preventDefault();try{document.getElementById('messages').click();}catch(e){}}
  else if ((e.altKey) && (e.key.toLowerCase() === 's')) {e.preventDefault();try{document.getElementById('system').click();}catch(e){}}
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
		else if(typeof SHORTCUT_MAP !== 'undefined' && SHORTCUT_MAP.constructor == Object && SHORTCUT_MAP !== null){
			let command = e.key.toLowerCase();command += e.altKey == true ? 'T': 'F';command += e.ctrlKey == true ? 'T': 'F';command += e.shiftKey == true ? 'T': 'F';
			if(SHORTCUT_MAP[command]){
        if(SHORTCUT_MAP[command].charAt(0) == '#'){
          e.preventDefault();
          try {document.getElementById(SHORTCUT_MAP[command].substr(1,SHORTCUT_MAP[command].length)).click();} catch(err){}
        }else if(SHORTCUT_MAP[command].charAt(0) == ':'){e.preventDefault();window[SHORTCUT_MAP[command].substr(1,SHORTCUT_MAP[command].length)]();}
      }
      // 4) ETAPA
      else{try{eventHandler(e);}catch(e){}}
    }
});