/******************************************************************************************
* Manibulação do modelo de dados DOCS
* Author: Rafael Gustavo F Alves [castelhano.rafael@gmail.com]
* Version: 1.00
*******************************************************************************************/

// let developer = new User('Rafael Gustavo Faria Alves', 'Rafael', 'castelhano.rafael@gmail.com');
// const query = window.location.search;
// const urlParams = new URLSearchParams(query);
// const version = urlParams.get('version');
// const view_type = urlParams.get('view_type') != null ? urlParams.get('view_type') : 'man';
// const target = urlParams.get('target') != null ? urlParams.get('target') : 'Core';

let docs = {};

// MONTA TODOS OS DOCUMENTOS EM _docs_base.json PARA O DICIONARIO docs
for(i=0;i < base.length;i++){
  d = new Docs();
  d.titulo = base[i].titulo;
  for(j=0;j < base[i].tags.length;j++){ // POPULANDO AS TAGS
    t = new Tag(base[i].tags[j].nome,base[i].tags[j].url,base[i].tags[j].class_list);
    d.tags.push(t);
  }
  for(j=0;j < base[i].topics.length;j++){ // POPULANDO OS TOPICS
    t = new Topic(base[i].topics[j].id,base[i].topics[j].titulo);
    d.topics.push(t);
    d.topics[j].body += d.topics[j].html();
    
    for(k=0;k < base[i].topics[j].htmlEls.length;k++){ // CARREGA OS ELEMENTOS HTML DO TOPICO
      t = new HtmlEL(base[i].topics[j].htmlEls[k].el,base[i].topics[j].htmlEls[k].innerHTML,base[i].topics[j].htmlEls[k].class_list,base[i].topics[j].htmlEls[k].auto_closed_tag);
      d.topics[j].htmlEls.push(t); // MONTA OS ELEMENTOS DA CLASSE HtmlEls
      d.topics[j].body +=  d.topics[j].htmlEls[k].html(); // PRINTA OS ELEMENTOS NO BODY DO TOPICS
    }
    
    for(k=0;k < base[i].topics[j].subtopics.length;k++){ // POPULANDO OS SUBTOPICOS DO TOPICO ALVO
      st = new Topic(base[i].topics[j].subtopics[k].id,base[i].topics[j].subtopics[k].titulo);
      d.topics[j].subtopics.push(st);
      d.topics[j].body += d.topics[j].subtopics[k].html('h5');
      
      for(l=0;l < base[i].topics[j].subtopics[k].htmlEls.length;l++){ // CARREGA OS ELEMENTOS DO SUBTOPICO
        t = new HtmlEL(base[i].topics[j].subtopics[k].htmlEls[l].el,base[i].topics[j].subtopics[k].htmlEls[l].innerHTML,base[i].topics[j].subtopics[k].htmlEls[l].class_list,base[i].topics[j].subtopics[k].htmlEls[l].auto_closed_tag);
        d.topics[j].subtopics[k].htmlEls.push(t); // MONTA OS ELEMENTOS DA CLASSE HtmlEls
        d.topics[j].body +=  d.topics[j].subtopics[k].htmlEls[l].html(); // PRINTA OS ELEMENTOS NO BODY DO TOPICS
      }
    }
  }
  for(j=0;j < base[i].issues.length;j++){ // MONTA TODOS OS ISSUES
    t = new Issue(base[i].issues[j].tipo, base[i].issues[j].titulo,base[i].issues[j].descricao,base[i].issues[j].solucao,base[i].issues[j].data_entrada,base[i].issues[j].usuario_entrada,base[i].issues[j].data_conclusao,base[i].issues[j].responsavel_conclusao,base[i].issues[j].status,base[i].issues[j].fechado);
    d.issues.push(t);
    d.issues_body +=  d.issues[j].html(); // PRINTA OS ELEMENTOS NO BODY DO ISSUES
  }
  docs[d.titulo] = d;
}

var doc_target = 'Core';
var view_type = 'man';

/* FUNCAO PRINCIPAL PARA CONSTRUÇÃO DA INTERFACE
** ACIONA FUNÇÃO AUXILIARES BASEDO NO doc_target (documento a ser exibido) E NA VARIAVEL view_type(man ou issues)
*/
function doc_build(view, target=doc_target){
  rebuild_index = target == doc_target ? false : true; // MARCA PARA RECRIAR A TABELA DE INDICES CASO SELECIONE OUTRO MANUAL
  view_type = view;
  doc_target = target;
  
  if(view_type == 'man'){
    man_elements_draw(docs[doc_target]);
    if(rebuild_index){layout_draw(docs[doc_target]);} // CASO TENHA ALTERADO O DOCUMENTO REFAZ OS INDICES
    document.getElementById('body_nav_container').classList.remove('d-none'); // REEXIBE A DIV DOS INDICES CASO OCULTA
    document.getElementById('man_link_btn').classList.add('active');
    document.getElementById('issues_link_btn').classList.remove('active');
  }
  else if(view_type == 'issues'){
    document.getElementById('body_nav_container').classList.add('d-none');
    issues_draw(docs[doc_target]);
    document.getElementById('issues_link_btn').classList.add('active');
    document.getElementById('man_link_btn').classList.remove('active');
  }
}

doc_build('man','Core'); // MONTA A PAGINA PELA PRIMEIRA VEZ COM O DOC PADRAO
layout_draw(docs[doc_target]); // MONTA OS INDICES, BADGE E DEMAIS ESTRUTURAS PELA PRIMEIRA VEZ PARA O DOC PADRAO


/* FUNCAO PARA CONSTRUÇÃO DO INDICE, CONTEINER DOS BADGES
** EH CHAMADA SOMENTE QUANDO O doc_target EH ALTERADO
*/
function layout_draw(doc){
  document.getElementById('nav_container').innerHTML = '';
  document.getElementById('nav_tags').innerHTML = '';
  document.getElementById('issues_badge').innerHTML = doc.issues.length;
  document.getElementById('doc_breadcrumb').innerHTML = doc.titulo;
  document.getElementById('doc_titulo').innerHTML = doc.titulo;
  for(i=0;i<doc.topics.length;i++){
    document.getElementById('nav_container').innerHTML += `<li class="text-primary pointer" onclick="goTo('${doc.topics[i].id}');">${doc.topics[i].titulo}</a>`;
    
    let subtopic_body = '';
    for(j=0;j < doc.topics[i].subtopics.length;j++){
      subtopic_body += `<li class="text-primary pointer" onclick="goTo('${doc.topics[i].subtopics[j].id}');">${doc.topics[i].subtopics[j].titulo}</a>`;
    }
    document.getElementById('nav_container').innerHTML += `<li><ul class="list-unstyled ps-4">${subtopic_body}</ul></li>`;
  }
  
  for(i=0;i<doc.tags.length;i++){
    if(doc.tags[i].url != ''){
      document.getElementById('nav_tags').innerHTML += `<a class="me-1 text-decoration-none ${doc.tags[i].class_list}" href="${doc.tags[i].url}" target="_blank">${doc.tags[i].nome}</a>`;
    }
    else{
      document.getElementById('nav_tags').innerHTML += `<span class="me-1 ${doc.tags[i].class_list}">${doc.tags[i].nome}</span>`;
    }
  }
};

/* FUNCAO PARA CONSTRUÇÃO DOS ELEMENTOS DO CORPO DO MANUAL
**
*/
function man_elements_draw(doc){
  document.getElementById('body_elements_container').innerHTML = '';
  for(i=0;i<doc.topics.length;i++){
    document.getElementById('body_elements_container').innerHTML += doc.topics[i].body;
  }
};

/* FUNCAO PARA CONSTRUÇÃO DOS ISSUES
**
*/
function issues_draw(doc){
  // document.getElementById('body_elements_container').innerHTML = '<table id="main_table" class="table border table-striped table-hover"><thead><tr><th>Tipo</th><th class="d-none d-md-table-cell">Titulo</th><th class="d-none d-lg-table-cell">Entrada</th><th class="d-none d-lg-table-cell">Usuario</th><th>Status</th></tr></thead><tbody>' + doc.issues_body + '</tbody></table>';
  document.getElementById('body_elements_container').innerHTML = doc.issues_body;
};