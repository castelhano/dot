window.jsPDF = window.jspdf.jsPDF;

class jsMdview{
    constructor(options){
        this.editor;
        this.previewTarget;
        this.container = options?.container || document.body; // Container para criacao do editor
        this.value = options?.value || ''; // Valor inicial a ser carregado no editor
        this.livePreview = options?.livePreview != undefined ? options.livePreview : true;
        this.autofocus = options?.autofocus != undefined ? options.autofocus : false;
        this.shortcuts = options?.shortcuts != undefined ? options.shortcuts : true;
        this.extra = options?.extra || []; // Botoes adicionais definidos no cliente
        this.db = options?.db || {}; // Padroes regex a serem aplicados no doc
        this.modelos = options?.modelos || {}; // Modelos de documento fornecidos pelo cliente
        this.minHeight = options?.minHeight || 700;
        // *************
        this.buildControls();
        this.build();
        this.__buildClientModels(); // Carrega modelos de documentos
        if(this.extra.length > 0){this.__loadExtra()}; // Adiciona botoes customizados pelo cliente
        if(this.shortcuts){this.__addShortcutMap()}; // Adiciona integracao com lib listener.js para atalhos dos elementos do menu
        if(this.value != ''){this.parse()}

    }
    build() {
        let row = document.createElement('div');row.classList = 'row g-3';
        let c1 = document.createElement('div');c1.classList = 'col-lg';
        let c2 = document.createElement('div');c2.classList = 'col-lg';
        this.editor = document.createElement('textarea');this.editor.classList = 'form-control';this.editor.style = `min-height: ${this.minHeight}px;`;this.editor.value = this.value;
        if(this.autofocus){this.editor.setAttribute('autofocus','')}
        if(this.livePreview){this.editor.oninput = () => {this.parse()}}
        c1.appendChild(this.editor);
        row.appendChild(c1);
        this.previewTarget = document.createElement('div');this.previewTarget.classList = 'border rounded h-100 p-4';
        c2.appendChild(this.previewTarget);
        row.appendChild(c2);
        this.container.appendChild(row);
    }
    buildControls(){
        let custom_classlist = 'btn btn-sm btn-phanton-light rounded-pill';
        let dropdown_classlist = 'btn btn-sm btn-phanton-light dropdown-toggle';
        let menu_group = document.createElement('div');menu_group.classList = 'border rounded-pill bg-body-secondary px-3 py-2 px-lg-1 py-lg-1 mb-2';
        this.bold = document.createElement('button');this.bold.type = 'button';this.bold.classList = custom_classlist;this.bold.innerHTML = '<i class="fas fa-bold"></i>';this.bold.title = 'Negrito';
        this.bold.onclick = () => {this.__editorAdd(['**','**'], [2,2])}
        menu_group.appendChild(this.bold);
        this.italic = document.createElement('button');this.italic.type = 'button';this.italic.classList = custom_classlist;this.italic.innerHTML = '<i class="fas fa-italic" style="width: 12px"></i>';this.italic.title = 'Italico';
        this.italic.onclick = () => {this.__editorAdd(['*','*'], [1,1])}
        menu_group.appendChild(this.italic);
        this.underline = document.createElement('button');this.underline.type = 'button';this.underline.classList = custom_classlist;this.underline.innerHTML = '<i class="fas fa-underline" style="width: 12px"></i>';this.underline.title = 'Tachado';
        this.underline.onclick = () => {this.__editorAdd(['_-','-_'], [2,2])}
        menu_group.appendChild(this.underline);
        this.heading = document.createElement('button');this.heading.type = 'button';this.heading.classList = dropdown_classlist;this.heading.setAttribute('data-bs-toggle', 'dropdown');this.heading.innerHTML = '<i class="fas fa-heading me-1"></i>';this.heading.title = 'Titulos';
        this.heading_menu = document.createElement('ul');this.heading_menu.classList = 'dropdown-menu fs-7';
        let h1 = document.createElement('li');h1.classList = 'px-3 py-2 container';
        let h1_row = document.createElement('div');h1_row.classList = 'row text-center';
        this.h1_start = document.createElement('div');this.h1_start.classList = 'col-4 btn-phanton-light pointer fw-bold';this.h1_start.innerHTML = '<i class="fas fa-heading"></i>1';this.h1_start.onclick = () => {this.__editorAdd(['# ','','Titulo'], false, true)}
        this.h1_center = document.createElement('div');this.h1_center.classList = 'col-4 btn-phanton-light pointer';this.h1_center.innerHTML = '<i class="fas fa-align-center"></i>';this.h1_center.onclick = () => {this.__editorAdd(['#_ ','','Titulo'], false, true)}
        this.h1_end = document.createElement('div');this.h1_end.classList = 'col-4 btn-phanton-light pointer';this.h1_end.innerHTML = '<i class="fas fa-align-right"></i>';this.h1_end.onclick = () => {this.__editorAdd(['#__ ','','Titulo'], false, true)}
        let h2 = document.createElement('li');h2.classList = 'px-3 py-2 container';
        let h2_row = document.createElement('div');h2_row.classList = 'row text-center';
        this.h2_start = document.createElement('div');this.h2_start.classList = 'col-4 btn-phanton-light pointer fw-bold';this.h2_start.innerHTML = '<i class="fas fa-heading"></i>2';this.h2_start.onclick = () => {this.__editorAdd(['## ','','Subtitulo'], false, true)}
        this.h2_center = document.createElement('div');this.h2_center.classList = 'col-4 btn-phanton-light pointer';this.h2_center.innerHTML = '<i class="fas fa-align-center"></i>';this.h2_center.onclick = () => {this.__editorAdd(['##_ ','','Subtitulo'], false, true)}
        this.h2_end = document.createElement('div');this.h2_end.classList = 'col-4 btn-phanton-light pointer';this.h2_end.innerHTML = '<i class="fas fa-align-right"></i>';this.h2_end.onclick = () => {this.__editorAdd(['##__ ','','Subtitulo'], false, true)}
        let h3 = document.createElement('li');h3.classList = 'px-3 py-2 container';
        let h3_row = document.createElement('div');h3_row.classList = 'row text-center';
        this.h3_start = document.createElement('div');this.h3_start.classList = 'col-4 btn-phanton-light pointer fw-bold';this.h3_start.innerHTML = '<i class="fas fa-heading"></i>3';this.h3_start.onclick = () => {this.__editorAdd(['### ','','Titulo de Seção'], false, true)}
        this.h3_center = document.createElement('div');this.h3_center.classList = 'col-4 btn-phanton-light pointer';this.h3_center.innerHTML = '<i class="fas fa-align-center"></i>';this.h3_center.onclick = () => {this.__editorAdd(['###_ ','','Titulo de Seção'], false, true)}
        this.h3_end = document.createElement('div');this.h3_end.classList = 'col-4 btn-phanton-light pointer';this.h3_end.innerHTML = '<i class="fas fa-align-right"></i>';this.h3_end.onclick = () => {this.__editorAdd(['###__ ','','Titulo de Seção'], false, true)}
        h1_row.appendChild(this.h1_start);h1_row.appendChild(this.h1_center);h1_row.appendChild(this.h1_end);
        h2_row.appendChild(this.h2_start);h2_row.appendChild(this.h2_center);h2_row.appendChild(this.h2_end);
        h3_row.appendChild(this.h3_start);h3_row.appendChild(this.h3_center);h3_row.appendChild(this.h3_end);
        h1.appendChild(h1_row);h2.appendChild(h2_row);h3.appendChild(h3_row);
        this.heading_menu.appendChild(h1);this.heading_menu.appendChild(h2);this.heading_menu.appendChild(h3);
        menu_group.appendChild(this.heading);
        menu_group.appendChild(this.heading_menu);
        // ---------
        this.align_center = document.createElement('button');this.align_center.type = 'button';this.align_center.classList = custom_classlist;this.align_center.innerHTML = '<i class="fas fa-align-center"></i>';this.align_center.title = 'Parágrafo centralizado';
        this.align_center.onclick = () => {this.__editorAdd(['__ ',''], [3,0], true)}
        menu_group.appendChild(this.align_center);
        this.align_end = document.createElement('button');this.align_end.type = 'button';this.align_end.classList = custom_classlist;this.align_end.innerHTML = '<i class="fas fa-align-right"></i>';this.align_end.title = 'Parágrafo a direita';
        this.align_end.onclick = () => {this.__editorAdd(['___ ',''], [4,0], true)}
        menu_group.appendChild(this.align_end);
        let vr1 = document.createElement('span');vr1.classList = 'text-body-tertiary';vr1.innerHTML = '&nbsp;&nbsp;|&nbsp;&nbsp;';menu_group.appendChild(vr1);
        this.blockquote = document.createElement('button');this.blockquote.type = 'button';this.blockquote.classList = custom_classlist;this.blockquote.innerHTML = '<i class="fas fa-terminal"></i>';this.blockquote.title = 'Citação';
        this.blockquote.onclick = () => {this.__editorAdd(['> ',''], [2,0], true)}
        menu_group.appendChild(this.blockquote);
        this.blockbox = document.createElement('button');this.blockbox.type = 'button';this.blockbox.classList = custom_classlist;this.blockbox.innerHTML = '<b>[ ab ]</b>';this.blockbox.title = 'Caixa de texto';
        this.blockbox.onclick = () => {this.__editorAdd(['[[ ',' ]]'], [3,3], true)};menu_group.appendChild(this.blockbox);
        this.breakWord = document.createElement('button');this.breakWord.type = 'button';this.breakWord.classList = custom_classlist;this.breakWord.innerHTML = '<i class="fas fa-level-down-alt rotate-90 fs-6" style="width: 12px"></i>';this.breakWord.title = 'Quebra de linha';
        this.breakWord.onclick = () => {this.__editorAdd(['<br />','',''], false, false, false)};
        menu_group.appendChild(this.breakWord);
        this.hr = document.createElement('button');this.hr.type = 'button';this.hr.classList = custom_classlist;this.hr.innerHTML = '<b>---</b>';this.hr.title = 'Linha horizontal';
        this.hr.onclick = () => {this.__editorAdd(['--','',''], false, false)};menu_group.appendChild(this.hr);
        this.pagebreak = document.createElement('button');this.pagebreak.type = 'button';this.pagebreak.classList = custom_classlist;this.pagebreak.innerHTML = '<i class="fas fa-cut fs-6"></i>';
        this.pagebreak.onclick = () => {this.__editorAdd(['[break]','',''], false, true, false)};this.pagebreak.title = 'Quebra de página';menu_group.appendChild(this.pagebreak);
        if(Object.keys(this.db).length > 0){
            let userBtn = this.__buildClientData();
            menu_group.appendChild(this.__buildDefaultData());
            menu_group.appendChild(userBtn);
        }
        let vr2 = document.createElement('span');vr2.classList = 'text-body-tertiary';vr2.innerHTML = '&nbsp;&nbsp;|&nbsp;&nbsp;';menu_group.appendChild(vr2);
        if(!this.livePreview){
            this.refresh = document.createElement('button');this.refresh.type = 'button';this.refresh.classList = 'btn btn-sm btn-phanton-success circle-hover ms-1';this.refresh.innerHTML = '<i class="fas fa-sync"></i>';this.refresh.title = 'Atualizar Preview';
            this.refresh.onclick = () => {this.parse()};
            menu_group.appendChild(this.refresh);
        }
        if(this.shortcuts){
            this.shortcutsBtn = document.createElement('button');this.shortcutsBtn.type = 'button';this.shortcutsBtn.classList = custom_classlist;this.shortcutsBtn.innerHTML = '<i class="fas fa-keyboard"></i>';this.shortcutsBtn.title = 'Atalhos de teclado';
            this.shortcutsBtn.onclick = () => {this.__showKeymaps()};
            menu_group.appendChild(this.shortcutsBtn);
        }
        this.extraBtns = document.createElement('span');this.extraBtns.classList = 'ms-2';menu_group.appendChild(this.extraBtns);
        // ---------
        this.container.appendChild(menu_group);
    }
    __buildClientData(){
        let wrapper = document.createElement('span');
        let btn = document.createElement('button');btn.type = 'button';btn.classList = 'btn btn-sm btn-phanton-light dropdown-toggle';btn.innerHTML = '<i class="fas fa-database"></i>';btn.setAttribute('data-bs-toggle','dropdown');btn.title = 'Variáveis do modelo';
        let ul = document.createElement('ul');ul.classList = 'dropdown-menu fs-7';
        for(let key in this.db){
            let li = document.createElement('li');li.classList = 'dropdown-item pointer';li.innerHTML = key;
            li.onclick = () => {this.__editorAdd([`$(${key})`,'',''], false, false)};
            ul.appendChild(li);
        }
        wrapper.appendChild(btn);
        wrapper.appendChild(ul);
        return wrapper;
    }
    __buildClientModels(){
        let wrapper = document.createElement('span');
        let btn = document.createElement('button');btn.type = 'button';btn.classList = 'btn btn-sm btn-phanton-light dropdown-toggle';btn.innerHTML = '<i class="fas fa-scroll"></i>';btn.setAttribute('data-bs-toggle','dropdown');btn.title = 'Modelos';
        let ul = document.createElement('ul');ul.classList = 'dropdown-menu fs-7';
        for(let key in this.modelos){
            let li = document.createElement('li');li.classList = 'dropdown-item pointer';li.innerHTML = key;
            li.onclick = () => {this.editor.value = this.modelos[key];if(this.livePreview){this.parse()}};
            ul.appendChild(li);
        }
        if(ul.children.length == 0){
            let li = document.createElement('li');li.classList = 'dropdown-item disabled';li.innerHTML = 'Nenhum modelo fornecido';
            ul.appendChild(li);
        }
        wrapper.appendChild(btn);
        wrapper.appendChild(ul);
        this.extraBtns.appendChild(wrapper);
    }
    __buildDefaultData(){
        let data = { // Adiciona chaves padrao a this.db, cria o menu de entrada para estes e retorna elemento
            'hoje': dateToday(),
            'agora': timeNow()
        }
        let wrapper = document.createElement('span');
        let btn = document.createElement('button');btn.type = 'button';btn.classList = 'btn btn-sm btn-phanton-light dropdown-toggle';btn.innerHTML = '<i class="fas fa-code"></i>';btn.setAttribute('data-bs-toggle','dropdown');btn.title = 'Variaveis globais';
        let ul = document.createElement('ul');ul.classList = 'dropdown-menu fs-7';
        for(let key in data){
            this.db[key] = data[key];
            let li = document.createElement('li');li.classList = 'dropdown-item pointer';li.innerHTML = key.charAt(0).toUpperCase() + key.slice(1);
            li.onclick = () => {this.__editorAdd([`$(${key})`,'',''], false, false)};
            ul.appendChild(li);
        }
        // ---
        wrapper.appendChild(btn);
        wrapper.appendChild(ul);
        return wrapper;
    }
    __editorAdd(pre_pos,select=false,newline=false,allowPlot=true){ // Insere o texto fornecido na posicao do cursor
        let start = this.editor.selectionStart;
        let end = this.editor.selectionEnd;
        let text = this.editor.value;
        let len = text.length;
        let value = allowPlot && start != end ? text.substring(start, end) : pre_pos[2] == undefined ? 'texto' : pre_pos[2];
        
        let br = newline && !['\n',''].includes(text.substring(start - 1, start)) ? true : false;
        let br_txt = br ? '\n' : '';
        let br_len = br ? 1 : 0;
        
        this.editor.value = text.substring(0, start) + br_txt + `${pre_pos[0]}${value}${pre_pos[1]}` + text.substring(end, len);
        // Retornando o foco na posicao correta
        this.editor.selectionEnd = (end + value.length + pre_pos[0].length + br_len) - (end - start);
        if(select){this.editor.selectionStart = start + select[0] + br_len;}
        this.editor.focus();
        if(this.livePreview){this.parse()}
    }
    parse() { // Gera preview do md
        let result = this.editor.value
            .replace(/^### (.*$)/gim, '<h5>$1</h5>')
            .replace(/^###__ (.*$)/gim, '<h5 class="text-end">$1</h5>')
            .replace(/^###_ (.*$)/gim, '<h5 class="text-center">$1</h5>')
            .replace(/^## (.*$)/gim, '<h4>$1</h4>')
            .replace(/^##__ (.*$)/gim, '<h4 class="text-end">$1</h4>')
            .replace(/^##_ (.*$)/gim, '<h4 class="text-center">$1</h4>')
            .replace(/^#__(.*$)/gim, '<h2 class="text-end">$1</h2>')
            .replace(/^#_(.*$)/gim, '<h2 class="text-center">$1</h2>')
            .replace(/^# (.*$)/gim, '<h2>$1</h2>')
            .replace(/^___(.*$)/gim, '<p class="text-end m-0">$1</p>')
            .replace(/^__(.*$)/gim, '<p class="text-center m-0">$1</p>')
            .replace(/--[-]*?/gim, '<hr >')
            .replace(/^\> (.*$)/gim, '<blockquote class="ps-2 border-start border-3 border-dark-subtle" style="font-size: 1.15rem">$1</blockquote>')
            .replace(/\[\[(.*?)\]\]/gim, '<div class="px-2 py-1 border rounded bg-body-secondary my-2">$1</div>')
            .replaceAll('[break]', '<span data-role="page-break"></span>')
            .replace(/\*\*(.*?)\*\*/gim, '<b>$1</b>')
            .replace(/\*(.*?)\*/gim, '<i>$1</i>')
            .replace(/_-(.*?)-_/gim, '<u>$1</u>')
            .replace(/!\[(.*?)\]\((.*?)\)/gim, "<img alt='$1' src='$2' />")
            .replace(/\[(.*?)\]\((.*?)\)/gim, "<a href='$2' target='_blank'>$1</a>")
            .replace(/\[footer\](.*?)\[\/footer\]/gim, "<hr /><p class='text-center'>$1</p>")
            .replace(/\n/gm, '<br>')
        for(let key in this.db){result = result.replaceAll(`$(${key})`, this.db[key])} // Faz replace para os dados a serem atereados no doc
        this.previewTarget.innerHTML = result.trim();
    }
    get(){return this.editor.value}
    __addShortcutMap(){
        SHORTCUT_MAP['bFTF'] = () => {this.bold.click();}
        SHORTCUT_MAP['iFTF'] = () => {this.italic.click()}
        SHORTCUT_MAP['.FTF'] = () => {this.blockquote.click()}
        SHORTCUT_MAP['[FTF'] = () => {this.blockbox.click()}
        SHORTCUT_MAP['enterFTF'] = () => {this.breakWord.click()}
        SHORTCUT_MAP['/FTF'] = () => {this.pagebreak.click()}
        // Headers shortcuts --
        SHORTCUT_MAP['hFTF'] = () => {this.heading.click()}
        SHORTCUT_MAP['1FFF'] = () => {if(mdviewHopen(this)){this.h1_start.click()}}
        SHORTCUT_MAP['4FFF'] = () => {if(mdviewHopen(this)){this.h1_center.click()}}
        SHORTCUT_MAP['7FFF'] = () => {if(mdviewHopen(this)){this.h1_end.click()}}
        SHORTCUT_MAP['2FFF'] = () => {if(mdviewHopen(this)){this.h2_start.click()}}
        SHORTCUT_MAP['5FFF'] = () => {if(mdviewHopen(this)){this.h2_center.click()}}
        SHORTCUT_MAP['8FFF'] = () => {if(mdviewHopen(this)){this.h2_end.click()}}
        SHORTCUT_MAP['3FFF'] = () => {if(mdviewHopen(this)){this.h3_start.click()}}
        SHORTCUT_MAP['6FFF'] = () => {if(mdviewHopen(this)){this.h3_center.click()}}
        SHORTCUT_MAP['9FFF'] = () => {if(mdviewHopen(this)){this.h3_end.click()}}
        function mdviewHopen(self){return self.heading_menu.classList.contains('show') ? true : false;}
    }
    __showKeymaps(){
        let maps = {
            'Texto em <b>negrito</b>': 'Ctrl + B',
            'Texto em <i>italico</i>': 'Ctrl + I',
            'Citação': 'Ctrl + .',
            'Caixa de texto': 'Ctrl + [',
            'Quebra de linha': 'Ctrl + ENTER',
            'Quebra de página': 'Ctrl + /',
            '<b class="text-secondary">Menu de Titulos</b>': '<b class="text-secondary">Ctrl + H</b>',
            '[seguido] Titulo (esq cen dir)': '<b>1</b> ou <b>4</b> ou <b>7</b>',
            '[seguido] Subtitulo (esq cen dir)': '<b>2</b> ou <b>5</b> ou <b>8</b>',
            '[seguido] Seção (esq cen dir)': '<b>3</b> ou <b>6</b> ou <b>9</b>',
        }
        let result = '<table class="table table-sm table-striped caption-top fs-7"><caption><b>jsReport:</b> Atalhos de teclado</caption><thead><tr><th>Ação</th><th>Atalho</th></tr></thead><tbody>';
        for(let key in maps){result += `<tr><td>${key}</td><td>${maps[key]}</td></tr>`}
        result += '</tbody></table>';
        this.previewTarget.innerHTML = result;
    }
    __loadExtra(){
        let custom_classlist = 'btn btn-sm btn-phanton-light rounded-pill';
        for(let i = 0;i < this.extra.length;i++){
            let btn = document.createElement('button');btn.type = 'button';btn.classList = this.extra[i]?.classList || custom_classlist;btn.innerHTML = this.extra[i]?.innerHTML || '--';
            if(this.extra[i].id){btn.id = this.extra[i].id}
            btn.onclick = this.extra[i]?.onclick || (() => {console.log('NADA A EXIBIR')});
            this.extraBtns.appendChild(btn);
        }
    }
}