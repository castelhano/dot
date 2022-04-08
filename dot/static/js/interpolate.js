/*
* dotPlot Javascript interpolation
*
* @version  1.0
* @since    07/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Implementa interpolacao (simplificada) direto no document, buscando attr dot-data
* @param    {Dict} map Dicionario com nome da variavel e valor para interpolar bo doc
* @example  var map={'foo':55,'fei':22}; dotPlot(map); ou dotPlot(map, '--'); no html: <label dot-data="foo" mask="cur" translate='{"180":"06 meses"}' default="feii" prefix="R$" posfix="real-BR"></dotPlot>
* @info     !! Pode gerar conflito com urlPlot() use uma OU outra
* @see      {@link https://stackoverflow.com/questions/62382939/vanilla-htmljs-dynamic-interpolation}
*/
function dotPlot(map, if_null=''){
  let data_raw = if_null;
  let data = if_null;
  [...document.querySelectorAll("*[dot-data]")].forEach(el => {
    if(map[el.getAttribute('dot-data')] != undefined){
      data_raw = map[el.getAttribute('dot-data')];
      data = data_raw;
    }
    else if(el.getAttribute('default') != undefined){data = el.getAttribute('default');} // Caso nao localize correspondente verifica se elemenento tem valor default
    if(el.getAttribute('translate') != undefined){ // Verifica se valor precisa ser 'traduzido', se sim tenta fazer a trducao
      try{
        let translate_map = JSON.parse(el.getAttribute('translate'));
        if(translate_map[data] != undefined){data = translate_map[data];}
      }catch(e){} 
    }
    if(el.getAttribute('mask') != undefined){data = dataMask(data, el.getAttribute('mask'))} // Verufuca se valor rpecisa ser mascarado, caso sim chama funcao auxiliar
    if(el.getAttribute('prefix') != undefined){data = `${el.getAttribute('prefix')} ${data}`}
    if(el.getAttribute('posfix') != undefined){data = `${data} ${el.getAttribute('posfix')}`}
    el.innerText = data;
   })
}

/*
* urlPlot Javascript interpolation buscando variaveis na url
*
* @version  1.0
* @since    07/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @example  urlPlot(); ou urlPlot('--') no html: <label dot-data="foo" mask="cur" translate='{"180":"06 meses"}'></dotPlot>
* @info     !! Pode gerar conflito com dotPlot() use uma OU outra
* @see      {@link https://stackoverflow.com/questions/62382939/vanilla-htmljs-dynamic-interpolation}
*/
function urlPlot(if_null=''){
  let list = window.location.search.replace('?','').split('&').filter(n => n);
  let map = {};
  for(i=0;i < list.length;i++){map[list[i].split('=')[0]] = list[i].split('=')[1];}
  dotPlot(map, if_null);
}

/*
* dataMask Funcao auxiliar para maskarar dados
*
* @version  1.0
* @since    08/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {Generic} data Valor a ser mascarado
* @param    {String} format Formato da mascara
* @example  dataMask(value, 'cur');
* @depend   vendor/mask.js
*/
function dataMask(data, mask=''){
  try {
    if(mask == 'cur'){return VMasker.toMoney(parseFloat(data).toFixed(2))}
    else if(mask.match(/^0/) && mask.replace(/0/g,'') == ''){return data.padStart(mask.length,'0');} // ZFILL n times 00 ou 000 ou 00000
    return data; //Caso nao achar formato compativel retorna a data_raw
  }catch(e){return data;} 
}