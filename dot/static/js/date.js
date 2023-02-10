/*
* BIBLIOTECA COM FUNCOES COMUNS PARA OPERACAO COM DATA
*/

/*
* dateDelta Retorna dias entre dias datas
*
* @version  1.0
* @since    09/02/2023
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
* @example  let days = dateDelta(data1,data2);
*/
function dateDelta(d1,d2){
    try{
        let diff = d1.getTime() - d2.getTime();
        return Math.floor(diff / (1000*3600*24));}
    catch(e){return false}
}