/******************************************************************************************
* Operações do modelo de dados PROJETO
* Author: Rafael Gustavo F Alves [castelhano.rafael@gmail.com]
* Version: 1.00
*******************************************************************************************/

// PARAMETROS DE VIAGENS
	var INICIO_OPERACAO = '04:50', FIM_OPERACAO = '23:30', CICLO_PADRAO = 50;
	var IDA = 'I', VOLTA = 'V';
	var PRODUTIVA = '1', RESERVADO = '0', EXPRESSO = '2',SEMIEXPRESSO = '3', ACESSO = '5', RECOLHE = '6', REFEICAO = '7';
	// VIAGEM PRODUTIVA < 5
	// ACESSO RECOLHE == 5 || 6

// PARAMETROS DE PROJETO
	var MICROONIBUS = 'MC', MIDIONIBUS = 'MD', CONVENCIONAL = 'CV', PADRON = 'PD', ARTICULADO = 'AT', BIARTICULADO = 'BI', ESPECIAL = 'ES';
	var False = false, True = true; // CONVERSAO DO DJANGO PARA JAVASCRIPT
	var VIAGENS_PARA_POPULAR = 5;
	var USER = params.user;
  
// BASE FUNCTIONS
function crescente(a,b){return (a-b);};
function decrescente(a,b){return (b-a);};
function format2Digits(numero){return ("0" + numero).slice(-2)};
function horaGT(inicio,fim, dia_inico, diaFim){ // COMPARA SE hora final eh maior que inicial
	let horaInicio = parseInt(inicio.split(':')[0]) + parseInt(diaInicio * 24);
	let minutoInicio = parseInt(inicio.split(':')[1]);
	let horaFim = parseInt(fim.split(':')[0]) + parseInt(diaFim * 24);
	let minutoFim = parseInt(fim.split(':')[1]);
	if(horaFim > horaInicio){return true;}
	if(horaFim === horaInicio && minutoFim > (minutoInicio + 1)){return true;}
	return false;
};

function minutoAdd(horaInicial, dia){ // ADICIONA 1 MINUTO NA HORA ORIGINAL
	let hora = parseInt(horaInicial.split(':')[0]);
	let minuto = parseInt(horaInicial.split(':')[1]);
	if(minuto < 59){minuto++;}
	else{
		minuto = 0;
		if(hora < 23 ){hora++;}
		else{hora = 0;dia++;}
	}
	horaAjustada = format2Digits(hora) + ':' + format2Digits(minuto);
	return [horaAjustada,dia];
};
function minutoSub(horaInicial, dia){ // SUBTRAI 1 MINUTO NA HORA ORIGINAL
	let hora = parseInt(horaInicial.split(':')[0]);
	let minuto = parseInt(horaInicial.split(':')[1]);
	if(minuto > 0){minuto--;}
	else{
		minuto = 59;
		if(hora > 0 ){hora--;}
		else{hora = 23;dia--;}
	}
	let horaAjustada = this.fim = format2Digits(hora) + ':' + format2Digits(minuto);
	return [horaAjustada,dia];
};
function somaMinutos(horaInicial, dia, minutos){ // SOMA OS MINUTOS NA HORA INICIAL
	let hora = parseInt(horaInicial.split(':')[0]);
	let minuto = parseInt(horaInicial.split(':')[1]);
  let target = dia * 1440 + hora * 60 + minuto + minutos;
  let dias = Math.floor(target / 1440);
  let residual = target % 1400;
  let horas = Math.floor(residual / 60);
  let minutosAjustado = target - (dias * 1440 + horas * 60);
  let horaAjustada = format2Digits(horas) + ":" + format2Digits(minutosAjustado);
  return [horaAjustada,dias];
};

function diferencaHoras(inicial,final, diaInicio, diaFim){
	let horaInicio = parseInt(inicial.split(':')[0]);
	let minutoInicio = parseInt(inicial.split(':')[1]);
	let horaFim = parseInt(final.split(':')[0]);
	let minutoFim = parseInt(final.split(':')[1]);
  let target = (diaFim * 1440 + horaFim * 60 + minutoFim) - (diaInicio * 1440 + horaInicio * 60 + minutoInicio);
  let dias = Math.floor(target / 1440);
  let residual = target % 1400;
  let horas = Math.floor(residual / 60);
  let minutos = target - (dias * 1440 + horas * 60);
  let horaAjustada = format2Digits(horas) + ":" + format2Digits(minutos);
  return [horaAjustada,dias];
  
};
function viagemInicioMinutos(viagem){
	let horaInicio = parseInt(viagem.inicio.split(':')[0]);
	let minutoInicio = parseInt(viagem.inicio.split(':')[1]);
  horaInicio += viagem.diaInicio * 24;
	return (horaInicio * 60 + minutoInicio);
}
function converterMinutos(horaInicial, dias){
  let horaInicio = parseInt(horaInicial.split(':')[0]);
	let minutoInicio = parseInt(horaInicial.split(':')[1]);
  return (dias * 1440 + horaInicio * 60 + minutoInicio);
}

// MODEL VIAGEM **********************************************************************
function Viagem(){
	this.inicio = INICIO_OPERACAO, this.fim = '';
	this.sentido = IDA, this.tipo = PRODUTIVA;
	this.diaInicio = 0, this.diaFim = 0;

	this.plus = function(){ // ADICIONA 1 MINUTO NO FIM DA VIAGEM
		let resultado = minutoAdd(this.fim, this.diaFim);
		this.fim = resultado[0];
		this.diaFim = resultado[1];
		return true;
	};
	this.sub = function(){ // RETIRA 1 MINUTO NO FIM DA VIAGEM
		if(horaGT(this.inicio,this.fim,this.diaInicio,this.diaFim)){ // VERIFICA SE VIAGEM TEM PELO MENOS 1 MIN
			let resultado = minutoSub(this.fim, this.diaFim);
			this.fim = resultado[0];
			this.diaFim = resultado[1];
			return true;
		}
		return false;
	};
	this.movePlus = function(){ // AUMENTA 1 MIN TANTO NO INICIO QUANTO NO FIM
		let inicioAjustado = minutoAdd(this.inicio, this.diaInicio);
		let fimAjustado = minutoAdd(this.fim, this.diaFim);
		this.inicio = inicioAjustado[0];
		this.diaInicio = inicioAjustado[1];
		this.fim = fimAjustado[0];
		this.diaFim = fimAjustado[1];
		return true;
	};
	this.moveSub = function(){ // SUBTRAI 1 MIN TANTO NO INICIO QUANTO NO FIM
		let hora = parseInt(this.inicio.split(':')[0]);
		let minuto = parseInt(this.inicio.split(':')[1]);
		if(hora > 0 || ((hora === 0 && minuto > 0) || this.diaInicio >  0)){ // NAO MOVE CASO SEJA 00:00
			let inicioAjustado = minutoSub(this.inicio, this.diaInicio);
			let fimAjustado = minutoSub(this.fim, this.diaFim);
			this.inicio = inicioAjustado[0];
			this.diaInicio = inicioAjustado[1];
			this.fim = fimAjustado[0];
			this.diaFim = fimAjustado[1];
			return true;
		}
		return false;
	};
	this.singlePlusInit = function(){ // AUMENTA 1 MIN NO INICIO DA VIAGEM
		if(horaGT(this.inicio,this.fim,this.diaInicio,this.diaFim)){ // VERIFICA SE INICIO HORA INICIO EH MAIOR QUE FINAL EM PELO MENOS 1 MIN E TRATA ERRO NO CASO DE 00:00 FIM
			let resultado = minutoAdd(this.inicio, this.diaInicio);
      this.inicio = resultado[0];
			this.diaInicio = resultado[1];
			return true;
		}
		return false;
	};
	this.singleSubInit = function(){ // SUBTRAI 1 MIN NO INCIO DA VIAGEM 
		if(this.inicio != "00:00" || this.diaInicio > 0){
      let resultado = minutoSub(this.inicio, this.diaInicio);
      this.inicio = resultado[0];
      this.diaInicio = resultado[1];
      return true;
    }
		return false;
	};
	this.calculaFim = function(){ // FUNCAO PARA ADICAO DE NOVAS VIAGENS, SOMA O INICIO DA VIAGEM COM O CICLO PRE CADASTRADO
		let faixa = parseInt(this.inicio.split(':')[0]);
		let ciclo = 0;
		if(this.sentido == IDA){ciclo = linha.cicloIda[faixa];}
		else if(this.sentido == VOLTA){ciclo = linha.cicloVolta[faixa];}
		let resultado = somaMinutos(this.inicio, this.diaInicio, ciclo);
		this.fim = resultado[0];
		this.diaFim = resultado[1];
	};
	this.getCiclo = function(){ // RETORNA A QTDE DE MINUTOS ENTRE INICIO E FIM DA VIAGEM
		return (converterMinutos(this.fim, this.diaFim) - converterMinutos(this.inicio, this.diaInicio))
	};
	this.print = function(){console.log('INICIO: [' + this.diaInicio + ']' + this.inicio + ' FIM: [' + this.diaFim + '] ' + this.fim);};
}; // END MODEL VIAGEM

// MODEL CARRO **********************************************************************
function Carro(){
	this.classificacao = CONVENCIONAL, this.cobrador = false, this.inclusivo = true;
	this.viagens = [];
	//------------
	this.adicionaViagem = function(){
		if(this.viagens == ""){
			let viagem = new Viagem();
			viagem.calculaFim();
			this.viagens.push(viagem);
			return viagem;
		}
		else{ // ADICIONA VIAGEM NO FIM DA LISTA
			console.log('ENTREI carro.adicionaViagem');
			viagem = new Viagem();
			let resultado = somaMinutos(this.viagens[this.viagens.length-1].fim,this.viagens[this.viagens.length-1].diaFim,(this.viagens[this.viagens.length-1].sentido === IDA ? linha.intervaloIda : linha.intervaloVolta));
			viagem.inicio = resultado[0];
			viagem.diaInicio = resultado[1];
			viagem.calculaFim();
			viagem.sentido = this.viagens[this.viagens.length-1].sentido == IDA ? VOLTA : IDA;
			this.viagens.push(viagem);
			return viagem;
		}
	};
	this.simulaNovaViagem = function(){ // CALCULA INSERSAO DE NOVA VIAGEM POREM NAO ADICIONA NO ARRAY
		if(this.viagens == ""){
			let viagem = new Viagem();
			viagem.calculaFim();
			return viagem;
		}
		else{ // ADICIONA VIAGEM NO FIM DA LISTA
			viagem = new Viagem();
			let resultado = somaMinutos(this.viagens[this.viagens.length-1].fim,this.viagens[this.viagens.length-1].diaFim,(this.viagens[this.viagens.length-1].sentido === IDA ? linha.intervaloIda : linha.intervaloVolta));
			viagem.inicio = resultado[0];
			viagem.diaInicio = resultado[1];
			viagem.calculaFim();
			viagem.sentido = this.viagens[this.viagens.length-1].sentido == IDA ? VOLTA : IDA;
			return viagem;
		}
	};
	this.removeViagem = function(viagem){if(viagem > 0 || this.viagens.length > 1){this.viagens.splice(viagem,1);return true;};
	}; // APAGA A VIAGEM INFORMADA
	this.removeViagens = function(inicio){if(inicio > 0) this.viagens.splice(inicio);}; // APAGA TODAS AS VIAGENS A PARTIR DA INFORMADA
	this.plus = function(viagem){ // AUMENTA 1 MIN NA VIAGEM INFORMADA E MOVE AS POSTERIORES EM 1 MIN NO INICIO E NO FIM
		this.viagens[viagem].plus();
		for(i=viagem+1;i < this.viagens.length;i++){this.viagens[i].movePlus();}
		return true;
	};
	this.sub = function(viagem){ // SUBTRAI 1 MIN NO FIM DA VIAGEM ATUAL E MOVE AS POSTERIORES 1 MIN PRA TRAS
		if(this.viagens[viagem].getCiclo() > 1){
			this.viagens[viagem].sub();
			for(i=viagem+1;i < this.viagens.length;i++){this.viagens[i].moveSub();}			
			return true;
		}
		return false;
	};
	this.movePlus = function(viagem){ // AUMENTA 1 MIN NO INICIO E FIM DA VIAGENS E EM TODAS AS POSTERIORES
		for(i=viagem;i < this.viagens.length;i++){this.viagens[i].movePlus();}
		return true;
	};
	this.moveSub = function(viagem){ // SUBTRAI 1 MIN NO INICIO E NO FIM DA VIAGEM ATUAL E TODAS AS SEGUINTES
		if(viagem == 0){ // EH PRIMEIRA VIAGEM DO CARRO
			if(this.viagens[viagem].inicio != '00:00' || this.viagens[viagem].diaInicio > 0){ // SO MOVE SE INICIO FOR MAIOR Q HORA 00:00
				for(i=viagem;i < this.viagens.length;i++){this.viagens[i].moveSub();}return true;
      }
			return false;
		}
		else{ // NAO EH A PRIMEIRA VIAGEM DO CARRO
			let viagemAlvo = this.viagens[viagem].inicio;
			let diaViagemAlvo = this.viagens[viagem].diaInicio;
			let viagemAnterior = this.viagens[viagem-1].fim;
			let diaViagemAnterior = this.viagens[viagem-1].diaFim;
			if(horaGT(viagemAnterior,viagemAlvo,diaViagemAlvo,diaViagemAnterior)){
				for(i=viagem;i < this.viagens.length;i++){this.viagens[i].moveSub();}
        return true;
			}
			return false;
		}
	};
	this.singlePlusInit = function(viagem){ // AUMENTA 1 MIN NO INICIO DA VIAGEM ALVO
		this.viagens[viagem].singlePlusInit(); // NESTE ESCOPO NAO EH NECESSARIO VALIDACOES
		return true;
	};
	this.singlePlusEnd = function(viagem){ // AUMENTA 1 MIN NO FIM DA VIAGEM ALVO
		if(viagem === (this.viagens.length-1)){ // EH A ULTIMA VIAGEM DO CARRO
			this.viagens[viagem].plus();
		}
		else{
			let viagemAtual = this.viagens[viagem].fim;
			let viagemPosterior = this.viagens[viagem+1].inicio;
			if(horaGT(viagemAtual,viagemPosterior,this.viagens[viagem+1].diaInicio,this.viagens[viagem+1].diaFim)){this.viagens[viagem].plus();}
		}
	};
	this.singleSubInit = function(viagem){ // SUBTRAI 1 MIN INICIO DA VIAGEM ALVO
		if(viagem === 0){return this.viagens[viagem].singleSubInit();} // EH A PRIMEIRA VIAGEM DO CARRO
		else{ // EXISTE VIAGENS ANTERIORES
			let viagemAtual = this.viagens[viagem].inicio;
			let viagemAnterior = this.viagens[viagem-1].fim;
			if(horaGT(viagemAnterior,viagemAtual,this.viagens[viagem].diaInicio,this.viagens[viagem].diaFim)){return this.viagens[viagem].singleSubInit();}
			return false;
		}		
	};
	this.singleSubEnd = function(viagem){ // SUBTRAI 1 MIN NO FINAL DA VIAGEM ALVO
		return this.viagens[viagem].sub(); // NESTE ESCOPO NAO EH NECESSARIO VALIDACOES
	};
	this.jornada = function(){ // SOMA O TEMPO ENTRE A PRIMEIRA E ULTIMA VIAGENS
		if(this.viagens.length === 1){return this.viagens[0].getCiclo();} // CARRO TEM APENAS UMA VIAGEM
		else if(this.viagens.length > 1){ // TEM MAIS DE UMA VIAGEM
			let inicio = this.viagens[0].inicio;
			let fim = this.viagens[this.viagens.length - 1].fim
			return diferencaHoras(inicio,fim,this.viagens[this.viagens.length-1].diaInicio,this.viagens[this.viagens.length-1].diaFim);
		}
		
	}
	this.jornadaProdutiva = function(){ // SOMA O TEMPO EM VIAGENS PRODUTIVAS -> TIPO < 5
		let soma = 0;
		for(i=0;i < this.viagens.length;i++){
			if(this.viagens[i].tipo < 5){soma += this.viagens[i].getCiclo();}			
		}
		let horaTmp = Math.floor(soma / 60);
		let minutoTmp = soma % 60;
		return [soma,(format2Digits(horaTmp) + ":" + format2Digits(minutoTmp))];
	};
	this.intervalos = function(){ // RETORNA A SOMA DOS INTERVALOS ENTRE VIAGENS
		let soma = 0;
		for(i=0;i < this.viagens.length;i++){
			if(!(typeof this.viagens[i+1] === 'undefined')){ // VERIFICA SE EXISTE UMA VIAGEM POSTERIOR
				let inicio = this.viagens[i].fim;
				let fim = this.viagens[i+1].inicio;
				soma += diferencaHoras(inicio,fim,this.viagens[i+1].diaInicio,this.viagens[i+1].diaFim)[0];
			}}
			let horaTmp = Math.floor(soma / 60);
			let minutoTmp = soma % 60;
			return [soma,(format2Digits(horaTmp) + ":" + format2Digits(minutoTmp))];
	};
	this.refeicoes = function(){ // SOMA O TEMPO EM VIAGENS DO TIPO REFEICAO -> 7
		let soma = 0;
		for(i=0;i < this.viagens.length;i++){
			if(this.viagens[i].tipo == 7){soma += this.viagens[i].getCiclo();}			
		}
		let horaTmp = Math.floor(soma / 60);
		let minutoTmp = soma % 60;
		return [soma,(format2Digits(horaTmp) + ":" + format2Digits(minutoTmp))];
	};
	
	
}; // END MODEL CARRO

// MODEL LINHA **********************************************************************
function Linha(){
	this.codigo = params.linhaCodigo, this.nome = params.linhaNome;
	this.origem = params.linhaOrigem, this.destino = params.linhaDestino;
	this.acessoOrigem = params.linhaAcessoOrigem, this.acessoDestino = params.linhaAcessoDestino, this.recolheOrigem = params.linhaRecolheOrigem, this.recolheDestino = params.linhaRecolheDestino;
	this.cicloIda = cicloIda, this.cicloVolta = cicloVolta, this.referenciasIda = [], this.referenciasVolta = [];
	this.intervaloIda = params.linhaIntervaloIda, this.intervaloVolta = params.linhaIntervaloVolta;
	
	this.getCiclo = function(sentido,faixa){
		if(sentido === IDA){return this.cicloIda[faixa];}
		if(sentido === VOLTA){return this.cicloVolta[faixa];}
	};
	this.setCiclo = function(sentido, faixa, ciclo){
		if(sentido === IDA){this.cicloIda[faixa] = ciclo;}
		else if(sentido === VOLTA){this.cicloVolta[faixa] = ciclo;}
	};
};
// MODEL PROJETO **********************************************************************
function Projeto(){
	this.codigo = params.projetoCodigo;
	this.status = params.projetoStatus, this.diaTipo = params.projetoDiaTipo;
	this.carros = [], this.linha = null;
	//------------
	this.adicionaCarro = function(){ // ADICIONA CARRO AO PROJETO
		var tmpCarro = new Carro();
		if(this.carros.length > 0){ // JA EXISTE CARRO NO PROJETO, CALCULA A FREQUENCIA IDEAL PELA FROTA PARA ADICIONAR NOVA VIAGEM
			console.log('ENTREI projeto.adicionaCarro');
			let primeiraViagem = this.carros[this.carros.length - 1].viagens[0];
			let ultimaViagem = this.carros[this.carros.length - 1].viagens[this.carros[this.carros.length - 1].viagens.length - 1];
			let faixa = parseInt(ultimaViagem.fim.split(':')[0]);
			let ciclo = linha.getCiclo(IDA,faixa) + linha.getCiclo(VOLTA,faixa) + linha.intervaloIda + linha.intervaloVolta;
			let frota = this.carros.length + 1;
			let frequencia = parseInt(ciclo / frota);
			let proxima = somaMinutos(primeiraViagem.inicio,primeiraViagem.diaInicio,frequencia);
			let viagem = new Viagem();
			viagem.inicio = proxima[0];
			viagem.diaInicio = proxima[1];
			viagem.calculaFim();
			tmpCarro.viagens.push(viagem);			
		} 
		else{tmpCarro.adicionaViagem();}// CASO SEJA PRIMEIRO CARRO ADICIONA UMA VIAGEM COM ATRIBUTOS PADRAO
		this.carros.push(tmpCarro);
	};
	this.adicionaViagem = function(carro){ //ADICIONA VIAGEM AO CARRO ALVO
		console.log('ENTREI projeto.adicionaViagem');
		return this.carros[carro].adicionaViagem();
	};
	this.removeViagem = function(carro,viagem){return this.carros[carro].removeViagem(viagem,1);};
	this.removeViagens = function(carro,inicio){this.carros[carro].removeViagens(inicio);};
	this.removeCarro = function(carro){this.carros.splice(carro,1);};
	
	this.proximaViagem = function(carro,viagem){
		let atual = viagemInicioMinutos(this.carros[carro].viagens[viagem]);
		let sentido = this.carros[carro].viagens[viagem].sentido;
		let carroTarget = null;
		let viagemTarget = null;
		let pesoTarget = 100000;
		for(i=0;i < this.carros.length;i++){
			for(j=0;j < this.carros[i].viagens.length;j++){
				if(this.carros[i].viagens[j].sentido === sentido){
					let alvo = viagemInicioMinutos(this.carros[i].viagens[j]);
					if(!(i == carro && j == viagem) && (alvo >= atual && alvo < pesoTarget)){ // ACHOU UM CANDIDATO A PROXIMA VIAGEM
						if(alvo == atual && i < carro){} // TRATA ERRO DE EVENTO PRESO EM DUAS VIAGENS IGUAIS, SE PESO IGUAL SO ALTERA SE ID CARRO FOR MAIOR Q ATUAL
						else{carroTarget = i;viagemTarget=j;pesoTarget=alvo;}
					}
				}
			}
		} // SAI DOS FORs
		if(carroTarget != null && viagemTarget != null){return [carroTarget,viagemTarget];} // ACHOU VIAGEM POSTERIOR
		else{return [carro,viagem];} // NÂO ACHOU VIAGEM POSTERIOR
	};
	
	this.viagemAnterior = function(carro,viagem){
		let atual = viagemInicioMinutos(this.carros[carro].viagens[viagem]);
		let sentido = this.carros[carro].viagens[viagem].sentido;
		let carroTarget = null;
		let viagemTarget = null;
		let pesoTarget = -1;
		for(i=0;i < this.carros.length;i++){
			for(j=0;j < this.carros[i].viagens.length;j++){
				if(this.carros[i].viagens[j].sentido === sentido){
					let alvo = viagemInicioMinutos(this.carros[i].viagens[j]);
					if(!(i == carro && j == viagem) && (alvo <= atual && alvo >= pesoTarget)){ // ACHOU UM CANDIDATO A PROXIMA VIAGEM
						if(alvo == atual && i > carro){} // TRATA ERRO DE EVENTO PRESO EM DUAS VIAGENS IGUAIS, SE PESO IGUAL SO ALTERA SE ID CARRO FOR MAIOR Q ATUAL
						else{carroTarget = i;viagemTarget=j;pesoTarget=alvo;}
					}
				}
			}
		} // SAI DOS FORs
		if(carroTarget != null && viagemTarget != null){return [carroTarget,viagemTarget];} // ACHOU VIAGEM POSTERIOR
		else{return [carro,viagem];} // NÂO ACHOU VIAGEM POSTERIOR
	};
	
	this.getFrequencia = function(carro,viagem){
		let anterior = this.viagemAnterior(carro,viagem);
		if(anterior[0] == carro && anterior[1] == viagem){return '--';} // NAO EXISTE VIAGEM ANTERIOR
		else{
			let inicioAtual = this.carros[carro].viagens[viagem].inicio;
			let inicioAnterior = this.carros[anterior[0]].viagens[anterior[1]].inicio;
			return diferencaHoras(inicioAnterior,inicioAtual,this.carros[carro].viagens[viagem].diaInicio,this.carros[carro].viagens[viagem].diaFim)[0];			
		}
	};
	this.gerar = function(frota){ // APAGA O PROJETO ATUAL E CRIA NOVO PROJETO PARA A FROTA INFORMADA
		this.clean();
		let faixaInicio = parseInt(INICIO_OPERACAO.split(':')[0]);
		let ciclo = linha.getCiclo(IDA,faixaInicio) + linha.getCiclo(VOLTA,faixaInicio) + linha.intervaloIda + linha.intervaloVolta;
		let frequencia = parseInt(ciclo / frota);
		for(i=0;i < frota;i++){ // INSERIR CARROS
			let carroTmp = new Carro();
			if(i == 0){ // EH O PRIMEIRO CARRO DO PROJETO
				let viagemTmp = new Viagem();
				viagemTmp.inicio = INICIO_OPERACAO; // INSERE UMA VIAGEM COM INICIO = INICIO DE OPERACAO
				viagemTmp.calculaFim();
				carroTmp.viagens.push(viagemTmp); // INSERE A PRIMEIRA VIAGEM NO CARRO
			}
			else{ // EXISTEM OUTROS CARROS NO PROJETO, INSERE NOVO CARRO NA FREQUENCIA
				let viagemTmp = new Viagem();
				let resultado = somaMinutos(this.carros[i-1].viagens[0].inicio,this.carros[i-1].viagens[0].diaInicio,frequencia); // BUSCA A PRIMEIRA VIAGEM DO CARRO ANTERIOR
				viagemTmp.inicio = resultado[0]; // INICIA CARRO NA FREQUENCIA
				viagemTmp.diaInicio = resultado[1];
				viagemTmp.calculaFim();
				carroTmp.viagens.push(viagemTmp); // SOBE A PRIMEIRA VIAGEM DO NOVO CARRO
			}
			let concluir = false;
			let count = 1; // ARMAZENA A QUANTIDADE DE VIAGENS INSERIDA NO CARRO
			while(!concluir){ // INSERE VIAGENS NO CARRO ATE O FIM DE OPERACAO
				let novaViagem = carroTmp.simulaNovaViagem();
				if(horaGT(FIM_OPERACAO,novaViagem.inicio,novaViagem.diaInicio, novaViagem.diaFim) || novaViagem.diaFim > 0){concluir = true;} // PARA INSERCAO QUANDO CHEGAR NO FIM DE OPERACAO
				else{carroTmp.adicionaViagem();count++;} // ADICIONA VIAGEM AO CARRO E INCREMENTA CONTATOR
			}
			this.carros.push(carroTmp);					
		}
		
	};
	this.clean = function(){this.carros=[];}; // LIMPA PROJETO
};