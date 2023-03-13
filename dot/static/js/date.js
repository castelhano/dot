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

/*
* dateInputExtras Adiciona a todos os input[type=date] listeners para data atual, ou para somar ou subtrair datas dias
*
* @version  1.0
* @since    13/03/2022
* @desc     Com o foco no input, precionar a tecla "T" altera para data atual "-" reduz data em 1 dia, ou "+" aumenta data em 1 dia
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
*/
function dateInputExtra_start(){
    document.querySelectorAll('input[type=date]').forEach((el) => {
        el.onkeydown = (e) => {
            if(e.keyCode == 84){el.value = dotToday(0,0,0,true)} // Precionado a letra T, carrega data atual
            else{
                if(![107, 109].includes(e.keyCode)){return} // Se nao for teclas - ou + encerra bloco
                let current = Date.parse(el.value + ' 00:00') ? new Date(el.value + ' 00:00') : new Date();
                if(e.keyCode == 109){ // Precionado -
                    current.setDate(current.getDate() - 1);
                    el.value = `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2,'0')}-${String(current.getDate()).padStart(2, '0')}`;
                }
                if(e.keyCode == 107){ // Precionado +
                    current.setDate(current.getDate() + 1);
                    el.value = `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2,'0')}-${String(current.getDate()).padStart(2, '0')}`;
                }
            }
        }
    });
}
