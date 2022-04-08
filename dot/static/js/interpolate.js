/*
* dotPlot Javascript interpolation
*
* @version  1.0
* @since    07/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @desc     Implementa interpolacao (simplificada) direto no document, buscando attr dot-data
* @param    {Dict} map Dicionario com nome da variavel e valor para interpolar bo doc
* @example  var map={'foo':55,'fei':22}; dotPlot(map); ou dotPlot(map, '--');
* @see      {@link https://stackoverflow.com/questions/62382939/vanilla-htmljs-dynamic-interpolation}
*/
function dotPlot(map, if_null=''){
  [...document.querySelectorAll("*[dot-data]")].forEach(el => {
    if(map[el.getAttribute('dot-data')] != undefined){
      let data_raw = map[el.getAttribute('dot-data')];
      let data = data_raw;
      if(el.getAttribute('translate') != undefined){
        try{
          let translate_map = JSON.parse(el.getAttribute('translate'));
          if(translate_map[data_raw] != undefined){data = translate_map[data_raw]};
        }catch(e){} 
      }
      if(el.getAttribute('mask') != undefined){console.log('TEM MASK');}
      
      el.innerText = data;
    }
    else{el.innerText = if_null}
   })
}

/*
* urlPlot Javascript interpolation buscando variaveis na url
*
* @version  1.0
* @since    07/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @example  urlPlot(); ou urlPlot('--') no html: <label dot-data="foo" mask="cur" translate="{'180':'06 meses'}"></dotPlot>
* @see      {@link https://stackoverflow.com/questions/62382939/vanilla-htmljs-dynamic-interpolation}
*/
function urlPlot(if_null=''){
  let list = window.location.search.replace('?','').split('&').filter(n => n);
  let map = {};
  for(i=0;i < list.length;i++){map[list[i].split('=')[0]] = list[i].split('=')[1];}
  dotPlot(map, if_null);
}