// Funcoes para manipulacao e captura da url

/*
* updateUrl Adiciona (ou atualiza) parametro na url (metodo GET) 
*
* @version  1.0
* @since    10/02/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} uri URL alvo
* @param    {String} key Nome do parametro a ser atualizado na url
* @param    {String} value Valor do parametro
* @returns  {String} URL formatada com o novo parametro
* @example  updateUrl('foo.com', 'nome', 'rafael'); Retorna: foo.com?nome=rafael
*/
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

/*
* filter Funcao atualiza URL com parametro e recarrega pagina
*
* @version  1.0
* @since    10/02/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} filter Nome do parametro a ser atualizado na url
* @param    {String} value Valor do parametro
* @example  filter('nome', 'rafael')
*/
function filter(filter, value){location.href = updateUrl(window.location.href, filter, value);}

/*
* urlFilter Semelhante a filter() porem nao atualiza pagina corrente, deve ser informado nova url para adicionar parametro
*
* @version  1.0
* @since    12/03/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} url URL para redirecionamento
* @param    {String} filter Nome do parametro a ser atualizado na url
* @param    {String} value Valor do parametro
* @example  urlFilter('fei.com', 'nome', 'rafael')
*/
function urlFilter(url, filter, value){location.href = updateUrl(url, filter, value);}

/*
* filters() Atualiza url corrente com multiplos parametros 
*
* @version  1.0
* @since    10/02/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {Array} filters Lista [] com parametros a serem adicionados na url
* @param    {Array} values Lista [] com valores dos parametros
* @example  filters(['nome', 'email'], ['rafael', 'foo@gmail.com'])
*/
function filters(filters, values){let h = window.location.href;for(i=0;i < filters.length; i++){h = updateUrl(h , filters[i], values[i]);}location.href = h;}

/*
* urlRedirect Carrega os filtros na url atual para uma nova url
*
* @version  1.0
* @since    01/04/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} url URL para redirecionamento
* @example  urlRedirect('fei.com')
*/
function urlRedirect(url){location.href = url + window.location.search;}


/*
* urlHasParam Retorna se o parametro esta informado na url
*
* @version  1.0
* @since    10/02/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {String} param Nome do parametro
* @returns  {Bool} Retorno true se parametro estiver na url ou false caso nao
* @example  let param = urlHasParam('nome')
*/
function urlHasParam(param){
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.has(param);
}

/*
* urlParams Retorna string com todos os parametros da url
*
* @version  1.0
* @since    10/02/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @returns  {String} String com os parametros da url
* @example  let params = urlParams()
*/
function urlParams(){return window.location.search;}

/*
* urlSetFiltersActive | Para todos os paramentros da url, adiciona a classe 'active' ao classList do elemento correspondente
*
* @version  1.0
* @since    10/02/2022
* @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
* @param    {Dict} filters Dicionario com key sendo o parametro a ser analizado e value sendo o id do elemento a ser estilizado
* @example  urlSetFiltersActive({'nome':'id_nome_label','email':'id_nome_label'})
*/
function urlSetFiltersActive(filters){
  for(i in filters){
    if(i.includes('=') && urlParams().includes(i)){document.getElementById(filters[i]).classList.add('active');}
    else {if(urlHasParam(i)){document.getElementById(filters[i]).classList.add('active');}}}}