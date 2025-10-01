/*
* I18n      Biblioteca com funcionalidades para internalionalizacao de texto (require dot.js)
*           Basta adicionar lib, ao carregar pagina verifica se o idioma do navegador eh igual ao langDefault (pt-BT), se diferente, busca arquivo json para lang = navigator.language
*           Para alteracao manual do lang, use o metodo i18n_setLang('es-US')
* @version  1.3
* @since    22/02/2023
* @release  09/09/2024 [add i18n_setLang para alteracao manual]
* @release  10/05/2023 [add generic lang search]
* @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
* @desc     
*/
var __lang = navigator.language || navigator.userLanguage;
var __genericLang = __lang.includes('-') ? __lang.split('-')[0] : false;
var i18n_path = '/app_data/i18n'; 
const __langDefault = 'pt-BR';
const __defaultPrefix = 'pt';
var __langDB = {};

var __defaultDB = {}; // armazena banco 
document.querySelectorAll('[data-i18n]').forEach((el)=>{ // cria base de traducao para lang default
    let itemPath = el.dataset.i18n.split('.'); // array com path da chave no dict
    let target = __defaultDB; // armazena ultimo apontador dentro do dict
    for(let i = 0; i < itemPath.length; i++){
        if(!target.hasOwnProperty(itemPath[i])){
            if(i == itemPath.length - 1){target[itemPath[i]] =  el.hasAttribute('data-i18n-target') ? el.getAttribute(el.getAttribute('data-i18n-target')) : el.innerHTML}
            else{target[itemPath[i]] = {}}
        }
        target = target[itemPath[i]];
    }
})


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


function i18n_setLang(lang){ // altera manualmente o lang e atualiza traducao
    // if(__lang == lang){
    //     console.log(`i18n: ${lang} is already the language in use, escaping.`);
    //     return false;
    // }
    __lang = lang;
    __genericLang = __lang.includes('-') ? __lang.split('-')[0] : false;
    if(__lang == __langDefault){ // se lang == langDefault, apenas retorna dict para status original e chama metodo i18n_start
        console.log(`i18n: Restoring default language`);
        __langDB = {...__defaultDB};
        i18n_start();
        return false;
    }
    console.log(`i18n: Sending request to server at ${timeNow({showSeconds:true})}`);
    dotAppData(`${i18n_path}-${__lang}.json`).then((d) => {
        if(d != ''){
            __langDB = d;
            i18n_start();
        }
        else if(__genericLang && __genericLang != __defaultPrefix){ // Caso nao localize idioma especifico busca generico (en-DE busca en)
            console.log(`i18n: Not found data for ${__lang}, sending request for '${__genericLang}' at ${timeNow({showSeconds:true})} `);
            dotAppData(`${i18n_path}-${__genericLang}.json`).then((g) => {if(g != ''){
                console.log(`i18n: Found data for '${__genericLang}'`);
                __langDB = g;
                i18n_start();
            }})
        }
        else{
            console.log(`i18n: Not found data for ${__lang}, escaping translation, at ${timeNow({showSeconds:true})}`);
        }
    });
}
if(__lang != __langDefault){i18n_setLang(__lang)} // Se language do cliente for diferente da default, carrega base com traducoes
else{console.log('i18n: Default language, ending script...')}