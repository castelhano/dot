/*
* I18n      Biblioteca com funcionalidades para internalionalizacao de texto
*
* @version  1.0
* @since    22/02/2023
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
*/
const __lang = navigator.language || navigator.userLanguage;
const __langDefault = 'pt-BR';
var __langDB = {};


function i18n_start(){
    console.log(`i18n: Start translating at ${timeNow({showSeconds:true})}`);
    document.querySelectorAll('[data-i18n]').forEach((e) => {
        try{
            let result = e.dataset.i18n.split('.').reduce((previous, current) => previous[current], __langDB);
            if(e.getAttribute('data-i18n-target') == null){e.innerHTML =  result || e.innerHTML}
            else{e.setAttribute(e.getAttribute('data-i18n-target'), result || e.innerHTML)}
            if(!result){trow}
        }
        catch(error){console.log(`i18n: [ERROR] Entry [${e.dataset.i18n}] not found for (${__lang})`)}
    })
    console.log(`i18n: End translating at ${timeNow({showSeconds:true})}`);
}

if(__lang != __langDefault){ // Se language do cliente for diferente da default, carrega base com traducoes
    console.log(`i18n: Sending request to server at ${timeNow({showSeconds:true})}`);
    dotAppData(`/app_data/i18n__${__lang}.json`).then((d) => {
        if(d != ''){__langDB = d}
        i18n_start();        
    });
}