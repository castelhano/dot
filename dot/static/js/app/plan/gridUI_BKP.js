/******************************************************************************************
* Funções para manipulação visual do Grid
* Author: Rafael Gustavo F Alves [castelhano.rafael@gmail.com]
* Version: 1.00
*******************************************************************************************/

console.log('UI carregado');
function carregarComponentes(vazio){ // FUNCAO BASE PARA INICIO DO GRID
	// start();
	// reguaDraw();
	console.log('ENTREI carrega componentes');
	
	if(vazio){
		console.log('ENTREI IF');
		carroAdicionar();cursorMove(0,0);}
	else{rebuild();}
	// carregaPatamares();
	gridCentralizar();
};

var PIXELS = 4;
var GRID_ROLL_WIDTH = 240;
/****************************************************************************************
* COMBINAÇÕES SUGERIDAS PARA EXIBIÇÃO DO GRID
* PIXELS		  6		  5		  4		  3		  2
* G_ROLL_WID	360		300		240		180		120
*****************************************************************************************/
var GRADE_X = 800; // DIMENSÃO EM MINUTOS, 1440 PARA 1 DIA (24 HORAS)
var DRAW_START_Y = 20; // INICIO DO GRID DESCONTANDO O TAMANHO DA REGUA
var SCREEN_X = screen.availWidth; // TAMANHO HORIZONTAL DA TELA DO USUARIO
var SCREEN_Y = screen.availHeight; // TAMANHO HORIZONTAL DA TELA DO USUARIO
var CAR_SIZE = 50; // TAMANHO VERTICAL DO CARRO NA GRADE EM PIXELS
var CAR_SLOT = parseInt(SCREEN_Y / (CAR_SIZE + 10)); // ARMAZENA O TAMANHO DE CARROS DISPONIVEL NA TELA DO USUARIO
var CAR_START_VIEW = 0; // ARMAZENA O CARRO EXIBIDO NO INICIO DO GRID
// var CAR_END_VIEW = (CAR_SLOT + CAR_START_VIEW)-1; // ULTIMO CARRO SENDO EXIBIDO NO GRID
var EDGE_XR = parseInt((SCREEN_X)); // LIMITE HORIZONTAL PARA TRIGGER PARA ROLAR TELA PARA DIREITA
// var EDGE_XR = parseInt((SCREEN_X * 0.8)); // LIMITE HORIZONTAL PARA TRIGGER PARA ROLAR TELA PARA DIREITA
var EDGE_XL = 144; // LIMITE HORIZONTAL PARA TRIGGER PARA ROLAR TELA PARA ESQUERDA
var EDGE_YT = 3; // USADO NO METODO PARA CENTRALIZAR TELA
var EDGE_YB = (CAR_SLOT + CAR_START_VIEW)-2; // LIMITE HORIZONTAL PARA TRIGGER PARA ROLAR TELA PARA BAIXO

var CURSOR_X = -1; // ARMAZENA POSICAO HORIZONTAL DO CURSOR NO GRID
var CURSOR_Y = -1; // ARMAZENA POSICAO VERTICAL DO CURSOR NO GRID
var CURSOR_ML = 10;


function gridClean(){
	document.getElementById('grid-itens').innerHTML = '';
	document.getElementById('regua-I').innerHTML = '';
	document.getElementById('regua-V').innerHTML = '';
	document.getElementById('grid-carros').innerHTML = '';
	document.getElementById('grid-itens').innerHTML += component_cursor(); // ADICIONA O CURSOR
	
};

function gerar(){
	gridClean()
	// projeto.gerar(document.getElementById('frota_gerar').value);
	rebuild();
	// $('#modal-gerar').modal('hide');
}

function start(){ // MONTA OS COMPONENTES DA INERFACE
	let grid = document.getElementById('grid-itens');
	let regua = document.getElementById('grid-regua');
	regua.innerHTML += componentRegua(); // ADICIONA O REGUA
	grid.innerHTML += componentCursor(); // ADICIONA O CURSOR
};

function rebuild(){ // CONSTROI PROJETO NO GRID
	let carros = document.getElementById('grid-carros');
	let grid = document.getElementById('grid-itens');
	for(i=0;i < projeto.carros.length;i++){ // ADICIONA OS CARROS / VIAGENS DO PROJETO AO GRID
		carros.innerHTML += componentCar(i,DRAW_START_Y + (CAR_SIZE * i));
		for(j=0; j < projeto.carros[i].viagens.length;j++){ 
			let tipo = projeto.carros[i].viagens[j].tipo
			let sentido = projeto.carros[i].viagens[j].sentido
			let id = String(i) + String(j);
			let w = projeto.carros[i].viagens[j].getCiclo() * PIXELS;
			let y = (((i + 1) * CAR_SIZE));
			let horaInicio = parseInt(projeto.carros[i].viagens[j].inicio.split(':')[0]);
			let minutoInicio = parseInt(projeto.carros[i].viagens[j].inicio.split(':')[1]);
			let x = ((horaInicio * 60) + minutoInicio) * PIXELS;
			let estilo = 'default';
			if(tipo == PRODUTIVA && sentido == IDA){estilo = 'ida';}
			else if(tipo == PRODUTIVA && sentido == VOLTA){estilo = 'volta';}
			else if(tipo != PRODUTIVA){
				switch(tipo){
						case RESERVADO:estilo = 'reservado';break;
						case EXPRESSO:estilo = 'expresso';break;
						case SEMIEXPRESSO:estilo = 'semiexpresso';break;
						case ACESSO: estilo = 'acesso';break;
						case RECOLHE: estilo = 'recolhe';break;
						case REFEICAO: estilo = 'refeicao';break;
					}
			}
			grid.innerHTML += componentViagem(String(i)+String(j),i,estilo,w,x,y);
			let reguaSentido = document.getElementById('regua-' + sentido);
			reguaSentido.innerHTML += componentMarcadorFrequencia(String(i)+String(j),i,x,sentido);			
		}
	}
	cursorMove(0,0);
};

function componentCursor(){return '<div id="cursor" class="cursor"><img src="/static/img/cursor.png"></div>';};
function componentRegua(){return '<div id="regua" class="regua"></div>';};
function componentMarcadorFrequencia(id,carro,x,sentido){return '<div id="f' + id + '" carro="' + carro + '" class="marcador-frequencia marcador-frequencia-' + sentido + '" style="left:' + x + 'px; margin-left:' + (PIXELS - 1) + 'px"></div>';};
function componentCar(id,y){return '<div id="c' + id + '" class="carro" style="position:absolute;left:130px;top:' + y + 'px;">' + (id + 1) + '</div>';};
function componentViagem(id,carro,estilo,width,x,y){return '<div id="v' + id + '" class="viagem ' +  estilo + '" carro="' + carro + '" style="width:' + width + 'px;position: absolute;left:' + x + 'px;top:' + y + 'px;"></div>';};




function cursorMove(carro,viagem){
	if(CURSOR_X > -1 && CURSOR_X != carro){document.getElementById('c' + CURSOR_X).classList.remove('selected');}
	CURSOR_X = carro;
	CURSOR_Y = viagem;
	let horaInicio = parseInt(projeto.carros[carro].viagens[viagem].inicio.split(':')[0]);
	let minutoInicio = parseInt(projeto.carros[carro].viagens[viagem].inicio.split(':')[1]);
	let x = ((horaInicio * 60) + minutoInicio) * PIXELS;
	let y = (carro + 1) * CAR_SIZE;
	let cursor = document.getElementById("cursor");
	let cursor_w = 28;
	let cursor_h = 45;
	cursor.style.position = 'absolute';
	cursor.style.left = (x - cursor_w) + 'px';
	cursor.style.top = (y - cursor_h) + 'px';
	atualizaDisplay();
	document.getElementById('c' + CURSOR_X).classList.add('selected');
};

function atualizaDisplay(){
	let viagem = projeto.carros[CURSOR_X].viagens[CURSOR_Y];
	document.getElementById("display-inicio").innerHTML = viagem.inicio;
	document.getElementById("display-fim").innerHTML = viagem.fim;
	document.getElementById("display-ciclo").innerHTML = viagem.getCiclo();
	document.getElementById("display-frequencia").innerHTML = projeto.getFrequencia(CURSOR_X,CURSOR_Y);
};

function plus(){
	projeto.carros[CURSOR_X].plus(CURSOR_Y);
	for(i=CURSOR_Y;i < projeto.carros[CURSOR_X].viagens.length;i++){viagemDraw(CURSOR_X,i);}
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};
function sub(){
	projeto.carros[CURSOR_X].sub(CURSOR_Y);
	for(i=CURSOR_Y;i < projeto.carros[CURSOR_X].viagens.length;i++){viagemDraw(CURSOR_X,i);}
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};

function singlePlusInit(){
	projeto.carros[CURSOR_X].singlePlusInit(CURSOR_Y);
	viagemDraw(CURSOR_X,CURSOR_Y);
	cursorMove(CURSOR_X,CURSOR_Y);
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};

function singleSubInit(){
	projeto.carros[CURSOR_X].singleSubInit(CURSOR_Y);
	viagemDraw(CURSOR_X,CURSOR_Y);
	cursorMove(CURSOR_X,CURSOR_Y);
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};

function singlePlusEnd(){
	projeto.carros[CURSOR_X].singlePlusEnd(CURSOR_Y);
	viagemDraw(CURSOR_X,CURSOR_Y);
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};

function singleSubEnd(){
	projeto.carros[CURSOR_X].singleSubEnd(CURSOR_Y);
	viagemDraw(CURSOR_X,CURSOR_Y);
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};

function movePlus(){
	projeto.carros[CURSOR_X].movePlus(CURSOR_Y);
	for(i=CURSOR_Y;i < projeto.carros[CURSOR_X].viagens.length;i++){viagemDraw(CURSOR_X,i);}
	cursorMove(CURSOR_X,CURSOR_Y);
	atualizaDisplay();
	alteracoes_nao_salvas = true;
};
function moveSub(){
	if(projeto.carros[CURSOR_X].moveSub(CURSOR_Y)){ // MODELO RETORNA SE FOI POSSIVEL MOVER
		for(i=CURSOR_Y;i < projeto.carros[CURSOR_X].viagens.length;i++){viagemDraw(CURSOR_X,i);}
		cursorMove(CURSOR_X,CURSOR_Y);
		if(document.getElementById('cursor').getBoundingClientRect().x < EDGE_XL){gridMR();} // VERIFICA SE CURSOR ESTA PROXIMO AO LIMITE ESQUERDO, SE SIM ROLA O GRID PARA DIREITA
		atualizaDisplay();
		alteracoes_nao_salvas = true;		
	}	
};

function carroAdicionar(){ // ADICIONA CARRO (GRID + MODELO)
	console.log('Entrei UI carroAdicionar');
	projeto.adicionaCarro();
	let grid = document.getElementById('grid-itens');
	let carros = document.getElementById('grid-carros');
	let regua_ida = document.getElementById('regua-I');
	let i = projeto.carros.length - 1;
	grid.innerHTML += componentViagem(String(i)+'0',i,'ida',0,0,0); // INSERE UMA VIAGEM EM BRANCO NO GRID
	carros.innerHTML += componentCar(i,DRAW_START_Y + (CAR_SIZE * i));
	regua_ida.innerHTML += componentMarcadorFrequencia(String(i)+'0',i,0,IDA); // ADICIONA MARCADOR EM BRANCO
	viagemDraw(i,0); // DESENHA A VIAGEM NO GRID	
	alteracoes_nao_salvas = true;
};

function carroRemover(){ // REMOVE CARRO (GRID + MODELO)
	if(CURSOR_X > 0){ // OBRIGATORIO TER PELO MENOS UM CARRO NO PROJETO
		let carroGrid = document.getElementById('c' + CURSOR_X);
		let qtdeAjuste = (projeto.carros.length - (CURSOR_X + 1)); // QUANTOS CARROS PARA AJUSTAR NO GRID
		let viagensGrid = document.querySelectorAll('[carro="' + CURSOR_X + '"]');
		Array.prototype.forEach.call(viagensGrid, function(node){node.remove();}) // REMOVE AS VIAGENS E SOMBRAS DO GRID
		
		for(i=(CURSOR_X+1);i <= (qtdeAjuste + CURSOR_X); i++){ // AJUSTA ID (SEQUENCIA) MOSTRADO NO CARRO
			let alvo =  document.getElementById('c' + i);
			alvo.style.top = (parseInt(alvo.style.top.replace("px","")) - CAR_SIZE) + 'px';
			alvo.innerHTML = i;
			alvo.id = 'c' + (i - 1);
			let viagensAlvo = document.querySelectorAll('[carro="' + i + '"]');
			Array.prototype.forEach.call(viagensAlvo, function(node,count){ // AJUSTA OS ATRIBUTOS DAS VIAGENS DOS CARROS POSTERIORES AO REMOVIDO
				node.style.top = (parseInt(node.style.top.replace("px","")) - CAR_SIZE) + 'px'; // MOVE PARA CIMA
				node.id = 'v' + String(i-1) + String(count); // AJUSTA O ID DO OBJETO
				node.setAttribute("carro", i-1); // ALTERA O ATRIBUTO DATA PARA IDENTIFICACAO DO CARRO
			}) // MOVE AS VIAGENS DO ALVO PARA CIMA NO GRID
		}
		projeto.removeCarro(CURSOR_X); // REMOVE CARRO DO MODELO
		cursorMove(CURSOR_X - 1,0); // MOVE O CURSOR PARA O CARRO ANTERIOR
		carroGrid.remove(); // APAGA O CARRO DO GRID-CARROS
		alteracoes_nao_salvas = true;
	}
};
function proximoCarro(){ // MOVE CURSOR PARA PROXIMO CARRO
	if(projeto.carros.length > (CURSOR_X + 1)){ // VERIFICA SE EXISTE PROXIMO CARRO
		if(projeto.carros[CURSOR_X + 1].viagens.length == 1){cursorMove(CURSOR_X+1,0);} // SO EXISTE UMA VIAGEM NO PROXIMO CARRO, MOVE PARA O INICIO
		else{ // EXISTE MAIS DE UMA VIAGEM NO PROXIMO CARRO, ESCOLHE A VIAGEM MAIS PROXIMA DA ATUAL (SEMPRE ANTERIOR A ESTA)
			let pesoAtual = viagemPesoInicio(projeto.carros[CURSOR_X].viagens[CURSOR_Y]);
			let melhorViagem = 0;
			let melhorPeso = 0;
			let i = 0;
			let range = projeto.carros[CURSOR_X + 1].viagens.length;
			let stop = false;
			while(!stop && i < range){ // CORRE AS VIAGENS DO PROXIMO, SE VIAGEM FOR MAIOR QUE ATUAL PARA DE CORRER E APONTA A ANTERIOR A ESTA
				let pesoAlvo = viagemPesoInicio(projeto.carros[CURSOR_X + 1].viagens[i]);
				if(pesoAlvo > melhorPeso && pesoAlvo < pesoAtual){melhorViagem = i;melhorPeso = pesoAlvo;}
				if(pesoAlvo >= pesoAtual){stop = true;}
				i++;
			}
			cursorMove(CURSOR_X+1,melhorViagem);
		}
	}
	let CX = document.getElementById('cursor').offsetLeft;
	let GX = document.getElementById('grid-itens').offsetLeft;
	let MARGEM_R = 300;
	if(CURSOR_X >= (CAR_SLOT + CAR_START_VIEW - 1)){gridMT();} //VALIDA ESTOURO VERTICAL
	if(cursor.getBoundingClientRect().x < EDGE_XL){gridViewLimits();} //VALIDA ESTOURO ESQUERDA
	if(CX > (EDGE_XR - GX - MARGEM_R)){gridViewLimits();} //VALIDA ESTOURO DIREITA
};
function carroAnterior(){ // MOVE CURSOR PARA PROXIMO CARRO
	if(CURSOR_X > 0){ // VERIFICA SE EXISTE CARRO ANTERIOR
		if(projeto.carros[CURSOR_X - 1].viagens.length == 1){cursorMove(CURSOR_X-1,0);} // SO EXISTE UMA VIAGEM NO CARRO ANTERIOR, MOVE PARA O INICIO
		else{ // EXISTE MAIS DE UMA VIAGEM NO CARRO, ESCOLHE A VIAGEM MAIS PROXIMA DA ATUAL (SEMPRE ANTERIOR A ESTA)
			let pesoAtual = viagemPesoInicio(projeto.carros[CURSOR_X].viagens[CURSOR_Y]);
			let melhorViagem = 0;
			let melhorPeso = 0;
			let i = 0;
			let range = projeto.carros[CURSOR_X - 1].viagens.length;
			let stop = false;
			while(!stop && i < range){ // CORRE AS VIAGENS DO PROXIMO, SE VIAGEM FOR MAIOR QUE ATUAL PARA DE CORRER E APONTA A ANTERIOR A ESTA
				let pesoAlvo = viagemPesoInicio(projeto.carros[CURSOR_X - 1].viagens[i]);
				if(pesoAlvo > melhorPeso && pesoAlvo < pesoAtual){melhorViagem = i;melhorPeso = pesoAlvo;}
				if(pesoAlvo >= pesoAtual){stop = true;}
				i++;
			}
			cursorMove(CURSOR_X-1,melhorViagem);
		}
		let CX = document.getElementById('cursor').offsetLeft;
		let GX = document.getElementById('grid-itens').offsetLeft;
		let MARGEM_R = 300;
		if(CURSOR_X < CAR_START_VIEW){gridMB();} // VALIDA ESTOURO A VERTICAL
		if(cursor.getBoundingClientRect().x < EDGE_XL){gridViewLimits();} //VALIDA ESTOURO ESQUERDA
		if(CX > (EDGE_XR - GX - MARGEM_R)){gridViewLimits();} //VALIDA ESTOURO DIREITA
	}
};
function carroProximaViagem(){ // MOVE CURSOR PARA PROXIMA VIAGEM DO CARRO (SE EXISTIR)
	let carro = projeto.carros[CURSOR_X];
	let grid = document.getElementById('grid-itens');
	let regua = document.getElementById('grid-regua');
	let regua_i = document.getElementById('regua-I');
	let regua_v = document.getElementById('regua-V');
	let cursor = document.getElementById('cursor');
	let MARGEM_R = 300;
	if(carro.viagens.length > (CURSOR_Y + 1)){
		cursorMove(CURSOR_X,CURSOR_Y+1);
		let GX = grid.offsetLeft;
		let CX = cursor.offsetLeft;
		if(CX > (EDGE_XR - GX - MARGEM_R)){ // ESTOUROU O LIMITE A DIREITA
			let pixels_rolar = ((CX - EDGE_XR) + MARGEM_R);
			grid.style.left = -(pixels_rolar) + 'px';
			regua.style.left = -(pixels_rolar) + 'px';
			regua_i.style.left = -(pixels_rolar) + 'px';
			regua_v.style.left = -(pixels_rolar) + 'px';
		}
	}
};

function carroViagemAnterior(){ // MOVE CURSOR PARA VIAGEM ANTERIOR DO CARRO (SE EXISTIR)
	let cursor = document.getElementById('cursor');
	let grid = document.getElementById('grid-itens');
	let regua = document.getElementById('grid-regua');
	let regua_i = document.getElementById('regua-I');
	let regua_v = document.getElementById('regua-V');
	let GX = grid.offsetLeft;
	if(CURSOR_Y > 0){cursorMove(CURSOR_X,CURSOR_Y-1);}
	if(cursor.getBoundingClientRect().x < EDGE_XL){ // ESTOUROU O LIMITE A ESQUERDA
		let MARGIN_L = 30;
		let pixels_rolar = EDGE_XL - cursor.getBoundingClientRect().x + MARGIN_L;
		grid.style.left = (GX + pixels_rolar) + 'px';
		regua.style.left = (GX + pixels_rolar) + 'px';
		regua_i.style.left = (GX + pixels_rolar) + 'px';
		regua_v.style.left = (GX + pixels_rolar) + 'px';
	}	
};

function viagemAdicionar(){
	let viagem = projeto.adicionaViagem(CURSOR_X);
	let grid = document.getElementById('grid-itens');
	let seq = projeto.carros[CURSOR_X].viagens.length - 1;
	let estilo = 'default';
	if(viagem.tipo == PRODUTIVA && viagem.sentido == IDA){estilo = 'ida';}
	else if(viagem.tipo == PRODUTIVA && viagem.sentido == VOLTA){estilo = 'volta';}
	else if(viagem.tipo != PRODUTIVA){
		switch(viagem.tipo){
				case RESERVADO:estilo = 'reservado';break;
				case EXPRESSO:estilo = 'expresso';break;
				case SEMIEXPRESSO:estilo = 'semiexpresso';break;
				case ACESSO: estilo = 'acesso';break;
				case RECOLHE: estilo = 'recolhe';break;
				case REFEICAO: estilo = 'refeicao';break;
			}
	}
	let regua_sentido = document.getElementById('regua-' + viagem.sentido + '');
	grid.innerHTML += component_viagem(String(CURSOR_X)+String(seq),CURSOR_X,estilo,0,0,0); // INSERE UMA VIAGEM EM BRANCO NO GRID
	regua_sentido.innerHTML += component_marcador_frequencia(String(CURSOR_X)+String(seq),CURSOR_X,0,viagem.sentido); // ADICIONA MARCADOR EM BRANCO
	viagemDraw(CURSOR_X,seq);
	alteracoes_nao_salvas = true;
};

function viagemRemover(){ // REMOVE UNICA VIAGEM NO CARRO
	if(CURSOR_Y > 0){ // EXISTE VIAGEM ANTERIOR
		projeto.removeViagem(CURSOR_X,CURSOR_Y); // REMOVE VIAGEM NO OBJETO
		document.getElementById('v' + String(CURSOR_X) + String(CURSOR_Y)).remove(); // REMOVE A VIAGEM NO GRID
		document.getElementById('f' + String(CURSOR_X) + String(CURSOR_Y)).remove(); // REMOVE A SOMBRA DA VIAGEM
		if(projeto.carros[CURSOR_X].viagens.length == CURSOR_Y){ // REMOVEU A ULTIMA VIAGEM
			cursorMove(CURSOR_X,CURSOR_Y - 1);
		}
		else{ // EXISTEM VIAGENS POSTERIORES, NECESSARIO ALTERAR ATRIBUTOS ID E CARRO DAS VIAGENS
			for(i=CURSOR_Y;i < projeto.carros[CURSOR_X].viagens.length;i++){
				let alvo = document.getElementById('v' + String(CURSOR_X) + String(i+1));
				let sombra = document.getElementById('f' + String(CURSOR_X) + String(i+1));
				alvo.id = 'v' + String(CURSOR_X) + String(i); // AJUSTA O ID DA VIAGEM
				sombra.id = 'f' + String(CURSOR_X) + String(i); // AJUSTA O ID DA SOMBRA
				alvo.setAttribute("carro", i); // ALTERA O ATRIBUTO DATA PARA IDENTIFICACAO DO CARRO
				sombra.setAttribute("carro", i); // ALTERA O ATRIBUTO DATA PARA IDENTIFICACAO DO CARRO
			}
			cursorMove(CURSOR_X,CURSOR_Y - 1);
			alteracoes_nao_salvas = true;
		}
	}
	else if(projeto.carros[CURSOR_X].viagens.length > 1){ // EH A PRIMEIRA VIAGEM E EXISTE POSTERIORES
		projeto.removeViagem(CURSOR_X,CURSOR_Y);
		document.getElementById('v' + String(CURSOR_X) + String(CURSOR_Y)).remove();
		document.getElementById('f' + String(CURSOR_X) + String(CURSOR_Y)).remove();
		for(i=0;i < projeto.carros[CURSOR_X].viagens.length;i++){
			let alvo = document.getElementById('v' + String(CURSOR_X) + String(i+1));
			let sombra = document.getElementById('f' + String(CURSOR_X) + String(i+1));
			alvo.id = 'v' + String(CURSOR_X) + String(i); // AJUSTA O ID DO OBJETO
			sombra.id = 'f' + String(CURSOR_X) + String(i); // AJUSTA O ID DO OBJETO
			alvo.setAttribute("carro", CURSOR_X); // ALTERA O ATRIBUTO DATA PARA IDENTIFICACAO DO CARRO
			sombra.setAttribute("carro", CURSOR_X); // ALTERA O ATRIBUTO DATA PARA IDENTIFICACAO DO CARRO
		}
		cursorMove(CURSOR_X,CURSOR_Y);
		alteracoes_nao_salvas = true;
	}
};

function viagensRemover(){ // APAGA A VIAGEM ATUAL E TODAS AS VIAGENS POSTERIORES
	if(CURSOR_Y > 0){
		for(i=CURSOR_Y;i < projeto.carros[CURSOR_X].viagens.length;i++){
			document.getElementById('v' + String(CURSOR_X) + String(i)).remove();
			document.getElementById('f' + String(CURSOR_X) + String(i)).remove();
		}
		projeto.removeViagens(CURSOR_X,CURSOR_Y);	
		cursorMove(CURSOR_X,CURSOR_Y-1);
		alteracoes_nao_salvas = true;
	}
};

function projetoProximaViagem(){ // MOVE CURSOR PARA PROXIMA VIAGEM "NO MESMO SENTIDO", INDIFERENTE DO CARRO
	let proxima = projeto.proximaViagem(CURSOR_X,CURSOR_Y);
	cursorMove(proxima[0],proxima[1]);
	gridViewLimits();
};
function projetoViagemAnterior(){ // MOVE CURSOR PARA VIAGEM ANTERIOR "NO MESMO SENTIDO", INDIFERENTE DO CARRO
	let anterior = projeto.viagemAnterior(CURSOR_X,CURSOR_Y);
	cursorMove(anterior[0],anterior[1]);
	gridViewLimits();
};

function viagemDraw(carro,viagem){ // ATUALIZA VIAGEM NO GRID
	let alvo = document.getElementById('v' + String(carro) + String(viagem));
	let sombra = document.getElementById('f' + String(carro) + String(viagem));
	let w = projeto.carros[carro].viagens[viagem].getCiclo() * PIXELS;
	let y = (((carro + 1) * CAR_SIZE));
	let horaInicio = parseInt(projeto.carros[carro].viagens[viagem].inicio.split(':')[0]);
	let minutoInicio = parseInt(projeto.carros[carro].viagens[viagem].inicio.split(':')[1]);
	let x = ((horaInicio * 60) + minutoInicio) * PIXELS;
	alvo.style.left = x + 'px';
	alvo.style.top = y + 'px';
	alvo.style.width = w + 'px';
	sombra.style.left =  x + 'px';
};


function gridCentralizar(){ // AJUSTA O GRID A POSICAO DO CURSOR
	let cursor = document.getElementById('cursor');
	let grid = document.getElementById('grid-itens');
	let regua = document.getElementById('grid-regua');
	let regua_i = document.getElementById('regua-I');
	let regua_v = document.getElementById('regua-V');
	let carros = document.getElementById('grid-carros');
	let MT = -5;
	let ML = -15;
	let GRID_DIF = (3 * PIXELS);
	let GX = parseInt(grid.style.left.replace('px',''));
	let GY = parseInt(grid.style.top.replace('px',''));
	let CX = parseInt(cursor.style.left.replace('px',''));
	let CY = parseInt(cursor.style.top.replace('px',''));
	if(CX > GX){grid.style.left = String(-CX-ML-GRID_DIF) + 'px';regua.style.left = String(-CX) + 'px';regua_i.style.left = String(-CX) + 'px';regua_v.style.left = String(-CX) + 'px';} // POSICIONAMENTO HORIZONTAL
	if(CY > GY){grid.style.top = String(-CY-MT) + 'px';carros.style.top = String(-CY-MT) + 'px';} // POSICIONAMENTO VERTICAL
	CAR_START_VIEW = CURSOR_X;
};

function gridViewLimits(){ // AJUSTA POSICAO GRID (projetoProximaViagem e projetoViagemAnterior)
	let cursor = document.getElementById('cursor');
	let grid = document.getElementById('grid-itens');
	let regua = document.getElementById('grid-regua');
	let regua_i = document.getElementById('regua-I');
	let regua_v = document.getElementById('regua-V');
	let carros = document.getElementById('grid-carros');
	let GX = grid.offsetLeft;
	let GY = grid.offsetTop;
	let CX = cursor.offsetLeft;
	let CY = cursor.offsetTop;
	
	if(CURSOR_X < CAR_START_VIEW){ // ESTOUROU LIMITE A CIMA
		let linhas_a_rolar = CURSOR_X - CAR_START_VIEW;
		let pixels_rolar = GY - (linhas_a_rolar * CAR_SIZE);
		let ajustado = Math.max(pixels_rolar,0);
		grid.style.top = ajustado + 'px';
		carros.style.top = ajustado + 'px';
		CAR_START_VIEW = CURSOR_X;
	}else if(CURSOR_X > (CAR_SLOT + CAR_START_VIEW - 1)){ // ESTOUROU LIMITE A BAIXO
		let linhas_a_rolar = CURSOR_X - EDGE_YB;
		let pixels_a_rolar = GY - (linhas_a_rolar * CAR_SIZE);
		grid.style.top = pixels_a_rolar + 'px';
		carros.style.top = pixels_a_rolar + 'px';
		CAR_START_VIEW += linhas_a_rolar;
	}
	let MARGEM_R = 300;
	if(CX > (EDGE_XR - GX - MARGEM_R)){ // ESTOUROU O LIMITE A DIREITA
		let pixels_rolar = ((CX - EDGE_XR) + MARGEM_R);
		grid.style.left = -(pixels_rolar) + 'px';
		regua.style.left = -(pixels_rolar) + 'px';
		regua_i.style.left = -(pixels_rolar) + 'px';
		regua_v.style.left = -(pixels_rolar) + 'px';
	}else if(document.getElementById('cursor').getBoundingClientRect().x < EDGE_XL){ // ESTOUROU O LIMITE A ESQUERDA
		let MARGIN_L = 30;
		let pixels_rolar = EDGE_XL - document.getElementById('cursor').getBoundingClientRect().x + MARGIN_L;
		grid.style.left = (GX + pixels_rolar) + 'px';
		regua.style.left = (GX + pixels_rolar) + 'px';
		regua_i.style.left = (GX + pixels_rolar) + 'px';
		regua_v.style.left = (GX + pixels_rolar) + 'px';
	}	
}

function gridML(){ // MOVE O GRID PARA ESQUERDA
	let grid = document.getElementById('grid-itens');
	let regua = document.getElementById('grid-regua');
	let regua_i = document.getElementById('regua-I');
	let regua_v = document.getElementById('regua-V');
	let x_atual = parseInt(grid.style.left.replace('px',''));
	grid.style.left = (x_atual - GRID_ROLL_WIDTH) + 'px';
	regua.style.left = (x_atual - GRID_ROLL_WIDTH) + 'px';
	regua_i.style.left = (x_atual - GRID_ROLL_WIDTH) + 'px';
	regua_v.style.left = (x_atual - GRID_ROLL_WIDTH) + 'px';
};
function gridMR(){ // MOVE O GRID PARA DIREITA
	let grid = document.getElementById('grid-itens');
	if(grid.offsetLeft < 0){
		let regua = document.getElementById('grid-regua');
		let regua_i = document.getElementById('regua-I');
		let regua_v = document.getElementById('regua-V');
		let x_atual = parseInt(grid.style.left.replace('px',''));
		let x_calculado = Math.min(x_atual + GRID_ROLL_WIDTH,0);
		grid.style.left = x_calculado + 'px';
		regua.style.left = x_calculado + 'px';		
		regua_i.style.left = x_calculado + 'px';		
		regua_v.style.left = x_calculado + 'px';		
	}	
};
function gridMB(){ // MOVE O GRID PARA BAIXO
	let grid = document.getElementById('grid-itens');
	if(parseInt(grid.style.top.replace('px','')) < 0){
		let carros = document.getElementById('grid-carros');
		let y_atual = parseInt(grid.style.top.replace('px',''));
		grid.style.top = (y_atual + CAR_SIZE) + 'px';
		carros.style.top = (y_atual + CAR_SIZE) + 'px';
		CAR_START_VIEW -= 1;
	}
};
function gridMT(){ // MOVE O GRID PARA CIMA
	let grid = document.getElementById('grid-itens');
	if(((CAR_SLOT - 1) -  (projeto.carros.length - CAR_START_VIEW)) < 0){
		let carros = document.getElementById('grid-carros');
		let y_atual = parseInt(grid.style.top.replace('px',''));
		grid.style.top = (y_atual - CAR_SIZE) + 'px';
		carros.style.top = (y_atual - CAR_SIZE) + 'px';
		CAR_START_VIEW += 1;
	}
};

function reguaDraw(){ // MONTA A REGUA HORIZONTAL NO GRID
	var hora = 0, minuto = 0, thisTick = "", i = 0;	
	for(var counter = 0; counter < GRADE_X;counter++){	
		if(i === 0){thisTick = "<div class='tick tickMajor' style='margin-left: " + (PIXELS - 1) + "px;'></div><label class='tickLabel'>" + hora + "</label>";}
		else if(i === 30){thisTick = "<div class='tick tickMedium' style='margin-left: " + (PIXELS - 1) + "px;'></div>";}
		else{thisTick = "<div class='tick tickMinor' style='margin-left: " + (PIXELS - 1) + "px;'></div>";}
		minuto++;i++;
		if(i === 60){i = 0;hora++} // INCREMENTA O I E VERIFICA SE ELE JÁ ATINGIU 1 HORA, SE SIM REINICIA O I
		if(hora === 24){hora = 0};
		let regua = document.getElementById('regua');
		regua.innerHTML += thisTick;
		regua.style.width = GRADE_X * PIXELS;
	}
};

function carregaPatamares(){
	let container = document.getElementById('patamares_form');
	for(i=0;i < 24;i++){
		let row = '<div class="row mb-1">';
		let col1 = '<div class="col-2 pt-1">' + i + '</div>';
		let col2 = '<div class="col"><div class="input-group"><input id="pi' + i + '" class="form-control form-control-sm" type="text" value="' + ciclo_ida[i] + '" readonly><div class="input-group-append"><a class="btn btn-sm btn-info patamarBTN" target="pi' + i + '" operation="plus"><i class="fas fa-plus-square text-light"></i></a><a class="btn btn-sm btn-dark patamarBTN" target="pi' + i + '" operation="minus"><i class="fas fa-minus-square text-light"></i></a></div></div></div>';
		let col3 = '<div class="col"><div class="input-group"><input id="pv' + i + '" class="form-control form-control-sm" type="text" value="' + ciclo_volta[i] + '" readonly><div class="input-group-append"><a class="btn btn-sm btn-info patamarBTN" target="pv' + i + '" operation="plus"><i class="fas fa-plus-square text-light"></i></a><a class="btn btn-sm btn-dark patamarBTN" target="pv' + i + '" operation="minus"><i class="fas fa-minus-square text-light"></i></a></div></div></div>';
		let col4 = '<div class="col"><div class="input-group"><input id="pf' + i + '" class="form-control form-control-sm frota_faixa_input" type="text" value="' + frotaFaixa[i] + '" readonly><div class="input-group-append"><a class="btn btn-sm btn-info patamarBTN" target="pf' + i + '" operation="plus"><i class="fas fa-plus-square text-light"></i></a><a class="btn btn-sm btn-dark patamarBTN" target="pf' + i + '" operation="minus"><i class="fas fa-minus-square text-light"></i></a></div></div></div>';
		let col5 = '<div class="col-2"><span id="pq' + i + '" class="d-inline-block mt-1">' + ((cicloIda[i] + cicloVolta[i] + linha.intervaloIda + linha.intervaloVolta) / frotaFaixa[i]).toFixed(2).replace('.',',') + '</span></div>';
		let fechaRow = '</div>';
		row += col1;row += col2;row += col3;row += col4;row += col5;row += fechaRow;
		container.innerHTML += row;
	}
	// document.getElementById('intervalo_ida').value = linha.intervalo_ida;
	// document.getElementById('intervalo_volta').value = linha.intervalo_volta;
	// document.getElementById('frota_gerar').value = projeto.carros.length;
};