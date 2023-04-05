
class jsReport{
    constructor(options){
        this.editor;
        this.previewTarget;
        this.container = options?.container || document.body; // Container para criacao do editor
        this.preview = options?.preview != undefined ? options.preview : true;
        this.autofocus = options?.autofocus != undefined ? options.autofocus : false;
        this.patterns = options?.patterns || {}; // Padroes regex a serem aplicados no doc
        this.db = options?.db || {}; // Padroes regex a serem aplicados no doc
        // *************
        this.buildControls();
        this.build();
    }
    build() {
        let row = document.createElement('div');row.classList = 'row g-3';
        let c1 = document.createElement('div');c1.classList = 'col-lg';
        let c2 = document.createElement('div');c2.classList = 'col-lg';
        this.editor = document.createElement('textarea');this.editor.classList = 'form-control';this.editor.style = 'min-height: 350px;';
        if(this.autofocus){this.editor.setAttribute('autofocus','')}
        c1.appendChild(this.editor);
        row.appendChild(c1);
        if(this.preview){
            this.previewTarget = document.createElement('div');this.previewTarget.classList = 'border rounded h-100 p-4';
            c2.appendChild(this.previewTarget);
            row.appendChild(c2);
        }
        this.container.appendChild(row);
    }
    buildControls(){
        let custom_classlist = 'btn btn-sm btn-phanton-light rounded-pill';
        let dropdown_classlist = 'btn btn-sm btn-phanton-light dropdown-toggle';
        let menu_group = document.createElement('div');menu_group.classList = 'border rounded-pill bg-body-secondary px-2 py-1 mb-2';
        let bold = document.createElement('button');bold.classList = custom_classlist;bold.innerHTML = '<i class="fas fa-bold fa-fw me-0"></i>';
        bold.onclick = () => {this.editor.value += '**texto** '}
        menu_group.appendChild(bold);
        let italic = document.createElement('button');italic.classList = custom_classlist;italic.innerHTML = '<i class="fas fa-italic fa-fw me-0"></i>';
        italic.onclick = () => {this.editor.value += '*texto* '}
        menu_group.appendChild(italic);
        let heading = document.createElement('button');heading.classList = dropdown_classlist;heading.setAttribute('data-bs-toggle', 'dropdown');heading.innerHTML = '<i class="fas fa-heading me-1"></i>';
        let heading_menu = document.createElement('ul');heading_menu.classList = 'dropdown-menu fs-7';
        let h1 = document.createElement('li');h1.classList = 'report-ddicon-list';
        let h1_row = document.createElement('div');h1_row.classList = 'row text-center';
        let h1_start = document.createElement('div');h1_start.classList = 'col-4 btn-phanton-light pointer fw-bold';h1_start.innerHTML = '<i class="fas fa-heading"></i>1';h1_start.onclick = () => {this.editor.value += this.editor.value == '' ? '# Titulo' : '\n# Titulo'}
        let h1_center = document.createElement('div');h1_center.classList = 'col-4 btn-phanton-light pointer';h1_center.innerHTML = '<i class="fas fa-align-center"></i>';h1_center.onclick = () => {this.editor.value += this.editor.value == '' ? '#_ Titulo' : '\n#_ Titulo'}
        let h1_end = document.createElement('div');h1_end.classList = 'col-4 btn-phanton-light pointer';h1_end.innerHTML = '<i class="fas fa-align-right"></i>';h1_end.onclick = () => {this.editor.value += this.editor.value == '' ? '#__ Titulo' : '\n#__ Titulo'}
        let h2 = document.createElement('li');h2.classList = 'report-ddicon-list';
        let h2_row = document.createElement('div');h2_row.classList = 'row text-center';
        let h2_start = document.createElement('div');h2_start.classList = 'col-4 btn-phanton-light pointer fw-bold';h2_start.innerHTML = '<i class="fas fa-heading"></i>2';h2_start.onclick = () => {this.editor.value += this.editor.value == '' ? '## Titulo' : '\n## Titulo'}
        let h2_center = document.createElement('div');h2_center.classList = 'col-4 btn-phanton-light pointer';h2_center.innerHTML = '<i class="fas fa-align-center"></i>';h2_center.onclick = () => {this.editor.value += this.editor.value == '' ? '##_ Titulo' : '\n##_ Titulo'}
        let h2_end = document.createElement('div');h2_end.classList = 'col-4 btn-phanton-light pointer';h2_end.innerHTML = '<i class="fas fa-align-right"></i>';h2_end.onclick = () => {this.editor.value += this.editor.value == '' ? '##__ Titulo' : '\n##__ Titulo'}
        let h3 = document.createElement('li');h3.classList = 'report-ddicon-list';
        let h3_row = document.createElement('div');h3_row.classList = 'row text-center';
        let h3_start = document.createElement('div');h3_start.classList = 'col-4 btn-phanton-light pointer fw-bold';h3_start.innerHTML = '<i class="fas fa-heading"></i>3';h3_start.onclick = () => {this.editor.value += this.editor.value == '' ? '### Titulo' : '\n### Titulo'}
        let h3_center = document.createElement('div');h3_center.classList = 'col-4 btn-phanton-light pointer';h3_center.innerHTML = '<i class="fas fa-align-center"></i>';h3_center.onclick = () => {this.editor.value += this.editor.value == '' ? '###_ Titulo' : '\n###_ Titulo'}
        let h3_end = document.createElement('div');h3_end.classList = 'col-4 btn-phanton-light pointer';h3_end.innerHTML = '<i class="fas fa-align-right"></i>';h3_end.onclick = () => {this.editor.value += this.editor.value == '' ? '###_ Titulo' : '\n###_ Titulo'}
        h1_row.appendChild(h1_start);h1_row.appendChild(h1_center);h1_row.appendChild(h1_end);
        h2_row.appendChild(h2_start);h2_row.appendChild(h2_center);h2_row.appendChild(h2_end);
        h3_row.appendChild(h3_start);h3_row.appendChild(h3_center);h3_row.appendChild(h3_end);
        h1.appendChild(h1_row);h2.appendChild(h2_row);h3.appendChild(h3_row);
        heading_menu.appendChild(h1);heading_menu.appendChild(h2);heading_menu.appendChild(h3);
        menu_group.appendChild(heading);
        menu_group.appendChild(heading_menu);
        // ---------
        let align_center = document.createElement('button');align_center.classList = custom_classlist;align_center.innerHTML = '<i class="fas fa-align-center fa-fw me-0"></i>';
        align_center.onclick = () => {this.editor.value += this.editor.value == '' ? '_ texto' : '\n_ texto'}
        menu_group.appendChild(align_center);
        let align_end = document.createElement('button');align_end.classList = custom_classlist;align_end.innerHTML = '<i class="fas fa-align-right fa-fw me-0"></i>';
        align_end.onclick = () => {this.editor.value += this.editor.value == '' ? '__ texto' : '\n__ texto'}
        menu_group.appendChild(align_end);
        let vr1 = document.createElement('span');vr1.classList = 'text-body-tertiary';vr1.innerHTML = '&nbsp;&nbsp;|&nbsp;&nbsp;';menu_group.appendChild(vr1);
        let blockquote = document.createElement('button');blockquote.classList = custom_classlist;blockquote.innerHTML = '<i class="fas fa-terminal fa-fw me-0"></i>';
        blockquote.onclick = () => {this.editor.value += this.editor.value == '' ? '> texto' : '\n> texto'}
        menu_group.appendChild(blockquote);
        let blockbox = document.createElement('button');blockbox.classList = custom_classlist;blockbox.innerHTML = '<b>[ ab ]</b>';blockbox.onclick = () => {this.editor.value += this.editor.value == '' ? '[[texto]]' : '\n[[texto]]'};menu_group.appendChild(blockbox);
        let hr = document.createElement('button');hr.classList = custom_classlist;hr.innerHTML = '<b>---</b>';
        hr.onclick = () => {this.editor.value += this.editor.value == '' ? '---' : '\n---'};menu_group.appendChild(hr);
        let pagebreak = document.createElement('button');pagebreak.classList = custom_classlist;pagebreak.innerHTML = '<i class="fas fa-cut fa-fw me-0 fs-6"></i>';pagebreak.onclick = () => {this.editor.value += this.editor.value == '' ? '[break]' : '\n[break]'};menu_group.appendChild(pagebreak);
        let vr2 = document.createElement('span');vr2.classList = 'text-body-tertiary';vr2.innerHTML = '&nbsp;&nbsp;|&nbsp;&nbsp;';menu_group.appendChild(vr2);
        let refresh = document.createElement('button');refresh.classList = 'btn btn-sm btn-phanton-success rounded-pill';refresh.innerHTML = '<i class="fas fa-sync fa-fw me-0"></i>';refresh.onclick = () => {this.parse()};menu_group.appendChild(refresh);
        // ---------
        this.container.appendChild(menu_group);


    }
    parse() {
        let result = this.editor.value
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^###__ (.*$)/gim, '<h3 class="text-end">$1</h3>')
            .replace(/^###_ (.*$)/gim, '<h3 class="text-center">$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^##__ (.*$)/gim, '<h2 class="text-end">$1</h2>')
            .replace(/^##_ (.*$)/gim, '<h2 class="text-center">$1</h2>')
            .replace(/^#__(.*$)/gim, '<h1 class="text-end">$1</h1>')
            .replace(/^#_(.*$)/gim, '<h1 class="text-center">$1</h1>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^__(.*$)/gim, '<p class="text-end">$1</p>')
            .replace(/^_(.*$)/gim, '<p class="text-center">$1</p>')
            .replace(/--[-]*/gim, '<hr >')
            .replace(/^\> (.*$)/gim, '<blockquote class="report-blockquote">$1</blockquote>')
            .replaceAll('[[', '<div class="report-block">')
            .replaceAll(']]', '</div>')
            .replaceAll('[break]', '<span class="html2pdf__page-break"></span>')
            .replace(/\*\*(.*)\*\*/gim, '<b>$1</b>')
            .replace(/\*(.*)\*/gim, '<i>$1</i>')
            .replace(/!\[(.*?)\]\((.*?)\)/gim, "<img alt='$1' src='$2' />")
            .replace(/\[(.*?)\]\((.*?)\)/gim, "<a href='$2' target='_blank'>$1</a>")
            .replace(/\n/gim, '<br>')
        for(let key in this.patterns){result = result.replace(key, this.patterns[key])} // Faz replace para os pattens definidos no cliente (caso algum)
        for(let key in this.db){result = result.replaceAll(key, this.db[key])} // Faz replace para os dados a serem atereados no doc
        if(this.preview){this.previewTarget.innerHTML = result.trim()}
        return result.trim();
    }
}