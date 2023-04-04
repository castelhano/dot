
class jsReport{
    constructor(options){
        this.editor;
        this.previewTarget;
        this.patterns = options?.patterns || {}; // Padroes regex a serem aplicados no doc
        this.db = options?.db || {}; // Padroes regex a serem aplicados no doc
    }
    build() {
        let row = document.createElement('div');row.classList = 'row g-3';
        let c1 = document.createElement('div');c1.classList = 'col-lg';
        let c2 = document.createElement('div');c2.classList = 'col-lg';
        // this.editor = 
    }
    parse() {
        let result = this.editor.value
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^###_ (.*$)/gim, '<h3 class="text-center">$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^##_ (.*$)/gim, '<h2 class="text-center>$1</h2>')
            .replace(/^#_(.*$)/gim, '<h1 class="text-center">$1</h1>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/^_(.*$)/gim, '<p class="text-center">$1</p>')
            .replace(/--[-]*/gim, '<hr >')
            .replace(/^\> (.*$)/gim, '<blockquote class="report-blockquote">$1</blockquote>')
            .replaceAll('[[', '<div class="report-block">')
            .replaceAll(']]', '</div>')
            .replace(/\*\*(.*)\*\*/gim, '<b>$1</b>')
            .replace(/\*(.*)\*/gim, '<i>$1</i>')
            .replace(/!\[(.*?)\]\((.*?)\)/gim, "<img alt='$1' src='$2' />")
            .replace(/\[(.*?)\]\((.*?)\)/gim, "<a href='$2'>$1</a>")
            .replace(/\n/gim, '<br>')
        for(let key in this.patterns){result = result.replace(key, this.patterns[key])} // Faz replace para os pattens definidos no cliente (caso algum)
        for(let key in this.db){result = result.replaceAll(key, this.db[key])} // Faz replace para os dados a serem atereados no doc
        if(this.previewTarget){this.previewTarget.innerHTML = result.trim()}
        return result.trim();
    }
}