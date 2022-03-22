/* UPDATE URL
** RAFAEL GUSTAVO 
** VERSÃO 1.0
** BIBLIOTECA DE OPERAÇÕES COM URL:
** updateUrl(): METODO INTERNO, ADICIONA OU ATUALIZA VALOR DE VARIAVEL NA URL
** filter(): INFORMA VARIAVEL E VALOR PARA ADIÇÃO (OU UPDATE) NA URL E SUBMETE PAGINA
** urlHasParam(): RETORNA BOOLEANO SE VARIAVEL ESTA PRESENTE NA URL
** urlParams(): RETORNA STRING COM TODOS OS PARAMETROS DA URL
** urlSetFiltersActive() METODO RECEBE UM DICIONARIO E MARCA COM CLASS active OS ID COM VARIAVEL CORRESPONDENTE NA URL (PASSOS A SEGUIR):
** 1) CRIE UM DICIONARIO COM A KEY SENDO O NOME DA VARIAVEL E O VALOR O ID DO ELEMENTO QUE VAI RECEBER A CLASS active
**    ex:   const = filters = {'meu_param':'id_meu_param'}
**    ex2:  const = filters = {'meu_param=Foo':'id_meu_param'} NESTE CASO VALIDA PARAMETRO + VALOR
**/
function updateUrl(uri, key, value) {
  var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
  var separator = uri.indexOf('?') !== -1 ? "&" : "?";
  if (uri.match(re)) {
    return uri.replace(re, '$1' + key + "=" + value + '$2');
  }
  else {
    return uri + separator + key + "=" + value;
  }
}
// USAGE: filter('nome', 'rafael')
function filter(filter, value){location.href = updateUrl(window.location.href, filter, value);}
function urlFilter(url, filter, value){location.href = updateUrl(url, filter, value);}
// USAGE: filters(['filtro1', 'filtro2'], ['foo', 'bar'])
function filters(filters, values){let h = window.location.href;for(i=0;i < filters.length; i++){h = updateUrl(h , filters[i], values[i]);}location.href = h;}
function urlHasParam(param){
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.has(param);
}
function urlParams(){return window.location.search;}
function urlSetFiltersActive(filters){
  for(i in filters){
    if(i.includes('=') && urlParams().includes(i)){document.getElementById(filters[i]).classList.add('active');}
    else {if(urlHasParam(i)){document.getElementById(filters[i]).classList.add('active');}}}}