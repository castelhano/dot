/******************************************************************************************
* Manibulação do modelo de dados DOCS
* Author: Rafael Gustavo F Alves [castelhano.rafael@gmail.com]
* Version: 1.00
*******************************************************************************************/

let developer = new User('Rafael Gustavo Faria Alves', 'Rafael', 'castelhano.rafael@gmail.com');

const query = window.location.search;
const urlParams = new URLSearchParams(query);
const version = urlParams.get('version');
const view_type = urlParams.get('view_type') != null ? urlParams.get('view_type') : 'manual';
const target = urlParams.get('target') != null ? urlParams.get('target') : 'core';

let doc = new Docs();
if(target == null || target == 'core'){
  doc.titulo = 'Core';
  doc.tags.push(new Tag('python','https://www.python.org/'), new Tag('django','https://www.djangoproject.com/'), new Tag('bootstrap5','https://getbootstrap.com/','badge bg-pink text-light'));
  p1 = new Topic('instalacao', 'Instalação');
  p1.subtopics.push(new Topic('instalacao_ambiente','Preparando o ambiente'));
  p1.subtopics.push(new Topic('instalacao_configuracoes','Configurações iniciais'));
  p1.subtopics.push(new Topic('instalacao_fixture','Carregando dados iniciais <b>(fixture)</b>'));
  i1 = new Issue();
  doc.topics.push(p1);
  i1.titulo = 'Manual do sistema incompleto';
  i1.descricao = 'Verificado que maior parte dos componentes do sistema permanece sem conteudo e detalhamento.';
  i1.data_entrada = '16/12/2021';
  i1.usuario_entrada = 'Rafael Alves';
  doc.issues.push(i1);
  
  if(view_type == 'manual'){
    el1 = new HtmlEL('p', 'Manual de utilização do sistema DOT, selecione o item desejado no <code class="fw-bold text-uppercase">indice</code> ou use a caixa de pesquisa, atalho <kbd>Ctrl+/</kbd>');
    el2 = new HtmlEL('div', 'Este eh um exemplo de um elemento callout', 'callout callout-warning');
    p1.add(el1.html());
    p1.add(el2.html());
  }
  else{
    p1.add('FOOOOO');
  }
  
}



function doc_draw(doc){
  document.getElementById('doc_breadcrumb').innerHTML = doc.titulo;
  document.getElementById('doc_titulo').innerHTML = doc.titulo;
  document.getElementById('issues_badge').innerHTML = doc.issues.length;
  for(i=0;i<doc.topics.length;i++){
    document.getElementById('nav_container').innerHTML += `<li class="text-primary pointer" onclick="goTo('${doc.topics[i].id}');">${doc.topics[i].titulo}</a>`;
    document.getElementById('body_elements_container').innerHTML += doc.topics[i].body;    
    let subtopic_body = '';
    for(j=0;j<doc.topics[i].subtopics.length;j++){subtopic_body += `<li class="text-primary pointer" onclick="goTo('${doc.topics[i].subtopics[j].id}');">${doc.topics[i].subtopics[j].titulo}</a>`;}
    document.getElementById('nav_container').innerHTML += `<li><ul class="list-unstyled ps-4">${subtopic_body}</ul></li>`;
  }
  for(i=0;i<doc.tags.length;i++){document.getElementById('nav_tags').innerHTML += `<a class="me-1 text-decoration-none ${doc.tags[i].class_list}" href="${doc.tags[i].url}" target="_blank">${doc.tags[i].nome}</a>`;}
};
doc_draw(doc);