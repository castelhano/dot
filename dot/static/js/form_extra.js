/* EXTRA_MASK_NUMBER
** LOCALIZA DECIMA OU INTEIRO PARA pt-BR (0.000,00)
** SE ELEMENTO ALVO TIVER ATRIBUTO value SETA RESULTADO NO VALUE, SE NAO NO innerHTML
*/
function extra_mask_number(el){
  if(el.hasAttribute('value')){el.value = (parseFloat(el.value)).toLocaleString("pt-BR");}
  else{el.innerHTML = (parseFloat(el.innerHTML)).toLocaleString("pt-BR");}
}

/* EXTRA_TODAY
** RETORNA A DATA ATUAL POSSIBILITANDO ADICAO (OU SUBTRACAO) DE DIAS, MESES E/OU ANOS
** SE ELEMENTO ALVO TIVER ATRIBUTO value SETA RESULTADO NO VALUE, SE NAO NO innerHTML
** native=true RETORNA DATA EM FORMATO NATIVO (yyyy-mm-aa)
*/
function extra_today(el, dias=0, meses=0, anos=0, native=false){
  var today = new Date();
  today.setDate(today.getDate() + dias);
  today.setMonth(today.getMonth() + meses + 1);
  today.setFullYear(today.getFullYear() + anos);
  const dd = String(today.getDate()).padStart(2, '0');
  const mm = String(today.getMonth()).padStart(2, '0');
  const yyyy = today.getFullYear();
  const hh = String(today.getHours()).padStart(2, '0');
  const ii = String(today.getMinutes()).padStart(2, '0');
  const ss = String(today.getSeconds()).padStart(2, '0');
  if(el.hasAttribute('value')){el.value = native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
  else{el.innerHTML = native == true ? `${yyyy}-${mm}-${dd}` : `${dd}/${mm}/${yyyy}`;}
}