window.jsPDF = window.jspdf.jsPDF;

class jsMdview{
    constructor(options){
        this.editor;
        this.previewTarget;
        this.container = options?.container || document.body; // Container para criacao do editor
        this.livePreview = options?.livePreview != undefined ? options.livePreview : true;
        this.autofocus = options?.autofocus != undefined ? options.autofocus : false;
        this.db = options?.db || {}; // Padroes regex a serem aplicados no doc
        this.minHeight = options?.minHeight || 700;
        // *************
        this.buildControls();
        this.build();
    }
    build() {
        let row = document.createElement('div');row.classList = 'row g-3';
        let c1 = document.createElement('div');c1.classList = 'col-lg';
        let c2 = document.createElement('div');c2.classList = 'col-lg';
        this.editor = document.createElement('textarea');this.editor.classList = 'form-control';this.editor.style = `min-height: ${this.minHeight}px;`;
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
        let menu_group = document.createElement('div');menu_group.classList = 'border rounded-pill bg-body-secondary px-2 py-1 mb-2';
        let bold = document.createElement('button');bold.type = 'button';bold.classList = custom_classlist;bold.innerHTML = '<i class="fas fa-bold"></i>';bold.title = 'Negrito';
        bold.onclick = () => {this.__editorAdd('**texto**', [2,2])}
        menu_group.appendChild(bold);
        let italic = document.createElement('button');italic.type = 'button';italic.classList = custom_classlist;italic.innerHTML = '<i class="fas fa-italic" style="width: 12px"></i>';italic.title = 'Italico';
        italic.onclick = () => {this.__editorAdd('*texto*', [1,1])}
        menu_group.appendChild(italic);
        let heading = document.createElement('button');heading.type = 'button';heading.classList = dropdown_classlist;heading.setAttribute('data-bs-toggle', 'dropdown');heading.innerHTML = '<i class="fas fa-heading me-1"></i>';heading.title = 'Titulos';
        let heading_menu = document.createElement('ul');heading_menu.classList = 'dropdown-menu fs-7';
        let h1 = document.createElement('li');h1.classList = 'px-3 py-2 container';
        let h1_row = document.createElement('div');h1_row.classList = 'row text-center';
        let h1_start = document.createElement('div');h1_start.classList = 'col-4 btn-phanton-light pointer fw-bold';h1_start.innerHTML = '<i class="fas fa-heading"></i>1';h1_start.onclick = () => {this.__editorAdd('# Titulo', [2,0], true)}
        let h1_center = document.createElement('div');h1_center.classList = 'col-4 btn-phanton-light pointer';h1_center.innerHTML = '<i class="fas fa-align-center"></i>';h1_center.onclick = () => {this.editor.value += this.editor.value == '' ? '#_ Titulo' : '\n#_ Titulo';if(this.livePreview){this.parse()}}
        let h1_end = document.createElement('div');h1_end.classList = 'col-4 btn-phanton-light pointer';h1_end.innerHTML = '<i class="fas fa-align-right"></i>';h1_end.onclick = () => {this.editor.value += this.editor.value == '' ? '#__ Titulo' : '\n#__ Titulo';if(this.livePreview){this.parse()}}
        let h2 = document.createElement('li');h2.classList = 'px-3 py-2 container';
        let h2_row = document.createElement('div');h2_row.classList = 'row text-center';
        let h2_start = document.createElement('div');h2_start.classList = 'col-4 btn-phanton-light pointer fw-bold';h2_start.innerHTML = '<i class="fas fa-heading"></i>2';h2_start.onclick = () => {this.editor.value += this.editor.value == '' ? '## Titulo' : '\n## Titulo';if(this.livePreview){this.parse()}}
        let h2_center = document.createElement('div');h2_center.classList = 'col-4 btn-phanton-light pointer';h2_center.innerHTML = '<i class="fas fa-align-center"></i>';h2_center.onclick = () => {this.editor.value += this.editor.value == '' ? '##_ Titulo' : '\n##_ Titulo';if(this.livePreview){this.parse()}}
        let h2_end = document.createElement('div');h2_end.classList = 'col-4 btn-phanton-light pointer';h2_end.innerHTML = '<i class="fas fa-align-right"></i>';h2_end.onclick = () => {this.editor.value += this.editor.value == '' ? '##__ Titulo' : '\n##__ Titulo';if(this.livePreview){this.parse()}}
        let h3 = document.createElement('li');h3.classList = 'px-3 py-2 container';
        let h3_row = document.createElement('div');h3_row.classList = 'row text-center';
        let h3_start = document.createElement('div');h3_start.classList = 'col-4 btn-phanton-light pointer fw-bold';h3_start.innerHTML = '<i class="fas fa-heading"></i>3';h3_start.onclick = () => {this.editor.value += this.editor.value == '' ? '### Titulo' : '\n### Titulo';if(this.livePreview){this.parse()}}
        let h3_center = document.createElement('div');h3_center.classList = 'col-4 btn-phanton-light pointer';h3_center.innerHTML = '<i class="fas fa-align-center"></i>';h3_center.onclick = () => {this.editor.value += this.editor.value == '' ? '###_ Titulo' : '\n###_ Titulo';if(this.livePreview){this.parse()}}
        let h3_end = document.createElement('div');h3_end.classList = 'col-4 btn-phanton-light pointer';h3_end.innerHTML = '<i class="fas fa-align-right"></i>';h3_end.onclick = () => {this.editor.value += this.editor.value == '' ? '###_ Titulo' : '\n###_ Titulo';if(this.livePreview){this.parse()}}
        h1_row.appendChild(h1_start);h1_row.appendChild(h1_center);h1_row.appendChild(h1_end);
        h2_row.appendChild(h2_start);h2_row.appendChild(h2_center);h2_row.appendChild(h2_end);
        h3_row.appendChild(h3_start);h3_row.appendChild(h3_center);h3_row.appendChild(h3_end);
        h1.appendChild(h1_row);h2.appendChild(h2_row);h3.appendChild(h3_row);
        heading_menu.appendChild(h1);heading_menu.appendChild(h2);heading_menu.appendChild(h3);
        menu_group.appendChild(heading);
        menu_group.appendChild(heading_menu);
        // ---------
        let align_center = document.createElement('button');align_center.type = 'button';align_center.classList = custom_classlist;align_center.innerHTML = '<i class="fas fa-align-center"></i>';align_center.title = 'Parágrafo centralizado';
        align_center.onclick = () => {
            this.editor.value += this.editor.value == '' ? '__ texto' : '\n__ texto';
            if(this.livePreview){this.parse()}
        }
        menu_group.appendChild(align_center);
        let align_end = document.createElement('button');align_end.type = 'button';align_end.classList = custom_classlist;align_end.innerHTML = '<i class="fas fa-align-right"></i>';align_end.title = 'Parágrafo a direita';
        align_end.onclick = () => {
            this.editor.value += this.editor.value == '' ? '___ texto' : '\n___ texto';
            if(this.livePreview){this.parse()}
        }
        menu_group.appendChild(align_end);
        let vr1 = document.createElement('span');vr1.classList = 'text-body-tertiary';vr1.innerHTML = '&nbsp;&nbsp;|&nbsp;&nbsp;';menu_group.appendChild(vr1);
        let blockquote = document.createElement('button');blockquote.type = 'button';blockquote.classList = custom_classlist;blockquote.innerHTML = '<i class="fas fa-terminal"></i>';blockquote.title = 'Citação';
        blockquote.onclick = () => {
            this.editor.value += this.editor.value == '' ? '> texto' : '\n> texto';
            if(this.livePreview){this.parse()}
        }
        menu_group.appendChild(blockquote);
        let blockbox = document.createElement('button');blockbox.type = 'button';blockbox.classList = custom_classlist;blockbox.innerHTML = '<b>[ ab ]</b>';blockbox.title = 'Caixa de texto';menu_group.appendChild(blockbox);
        blockbox.onclick = () => {
            this.editor.value += this.editor.value == '' ? '[[texto]]' : '\n[[texto]]';
            if(this.livePreview){this.parse()}
        }
        let breakWord = document.createElement('button');breakWord.type = 'button';breakWord.classList = custom_classlist;breakWord.innerHTML = '<i class="fas fa-level-down-alt rotate-90 fs-6" style="width: 12px"></i>';breakWord.title = 'Quebra de linha';
        breakWord.onclick = () => {this.editor.value += '<br />';if(this.livePreview){this.parse()}};menu_group.appendChild(breakWord);
        let hr = document.createElement('button');hr.type = 'button';hr.classList = custom_classlist;hr.innerHTML = '<b>---</b>';hr.title = 'Linha horizontal';
        hr.onclick = () => {this.editor.value += this.editor.value == '' ? '---' : '\n---';if(this.livePreview){this.parse()}};menu_group.appendChild(hr);
        let pagebreak = document.createElement('button');pagebreak.type = 'button';pagebreak.classList = custom_classlist;pagebreak.innerHTML = '<i class="fas fa-cut fs-6"></i>';pagebreak.onclick = () => {this.editor.value += this.editor.value == '' ? '[break]' : '\n[break]'};pagebreak.title = 'Quebra de página';menu_group.appendChild(pagebreak);
        if(Object.keys(this.db).length > 0){
            let userBtn = this.buildClientData();
            menu_group.appendChild(this.buildDefaultData());
            menu_group.appendChild(userBtn);
        }
        if(!this.livePreview){
            let vr2 = document.createElement('span');vr2.classList = 'text-body-tertiary';vr2.innerHTML = '&nbsp;&nbsp;|&nbsp;&nbsp;';menu_group.appendChild(vr2);
            let refresh = document.createElement('button');refresh.type = 'button';refresh.classList = 'btn btn-sm btn-phanton-success circle-hover ms-1';refresh.innerHTML = '<i class="fas fa-sync"></i>';refresh.title = 'Atualizar Preview';
            refresh.onclick = () => {this.parse()};
            menu_group.appendChild(refresh);
        }
        // ---------
        this.container.appendChild(menu_group);
    }
    buildClientData(){
        let wrapper = document.createElement('span');
        let btn = document.createElement('button');btn.type = 'button';btn.classList = 'btn btn-sm btn-phanton-light dropdown-toggle';btn.innerHTML = '<i class="fas fa-database"></i>';btn.setAttribute('data-bs-toggle','dropdown');btn.title = 'Variáveis do modelo';
        let ul = document.createElement('ul');ul.classList = 'dropdown-menu fs-7';
        for(let key in this.db){
            let li = document.createElement('li');li.classList = 'dropdown-item pointer';li.innerHTML = key;
            li.onclick = () => {this.editor.value += `$(${key})`;if(this.livePreview){this.parse()}};
            ul.appendChild(li);
        }
        wrapper.appendChild(btn);
        wrapper.appendChild(ul);
        return wrapper;
    }
    buildDefaultData(){
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
            li.onclick = () => {this.editor.value += `$(${key})`;if(this.livePreview){this.parse()}};
            ul.appendChild(li);
        }
        // ---
        wrapper.appendChild(btn);
        wrapper.appendChild(ul);
        return wrapper;
    }
    __editorAdd(text,select=false,newline=false){ // Insere o texto fornecido na posicao do cursor
        let start = this.editor.selectionStart;
        let end = this.editor.selectionEnd;
        let value = this.editor.value;
        let len = value.length;
        if(newline && value != ''){
            if(value.substring(start - 1, start) != '\n'){text = `\n${text}`}
        }
        this.editor.value = value.substring(0, start) + text + value.substring(end, len);
        // Retornando o foco na posicao correta
        this.editor.selectionEnd = (end + text.length - (end - start));
        if(select){
            this.editor.selectionStart = start + select[0];
            this.editor.selectionEnd -= select[1];
        }        
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
            .replace(/--[-]*/gim, '<hr >')
            .replace(/^\> (.*$)/gim, '<blockquote class="ps-2 border-start border-3 border-dark-subtle" style="font-size: 1.15rem">$1</blockquote>')
            .replace(/\[\[(.*?)\]\]/gim, '<div class="px-2 py-1 border rounded bg-body-secondary my-2">$1</div>')
            .replaceAll('[break]', '<span data-role="page-break"></span>')
            .replace(/\*\*(.*)\*\*/gim, '<b>$1</b>')
            .replace(/\*(.*)\*/gim, '<i>$1</i>')
            .replace(/!\[(.*?)\]\((.*?)\)/gim, "<img alt='$1' src='$2' />")
            .replace(/\[(.*?)\]\((.*?)\)/gim, "<a href='$2' target='_blank'>$1</a>")
            .replace(/\n/gim, '<br>')
        for(let key in this.db){result = result.replaceAll(`$(${key})`, this.db[key])} // Faz replace para os dados a serem atereados no doc
        this.previewTarget.innerHTML = result.trim();
    }
    get(){return this.editor.value}
}