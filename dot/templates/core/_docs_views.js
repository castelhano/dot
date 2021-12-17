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
const target = urlParams.get('target') != null ? urlParams.get('target') : 'Core';

let docs = {};

// Montando os documentos
// Percorre array base instanciada no layout docs.html

for(i=0;i < base.length;i++){ // CRIANDO DADOS BASO DO DOCUMENTO
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
    
    for(k=0;k < base[i].topics[j].htmlEls.length;k++){ // CARREGA OS ELEMENTOS DO TOPICO
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
  for(j=0;j < base[i].issues.length;j++){
    t = new Issue(base[i].issues[j].titulo,base[i].issues[j].descricao,base[i].issues[j].solucao,base[i].issues[j].data_entrada,base[i].issues[j].usuario_entrada,base[i].issues[j].data_conclusao,base[i].issues[j].responsavel_conclusao,base[i].issues[j].status,base[i].issues[j].fechado);
    d.issues.push(t);
  }
  docs[d.titulo] = d;
}

if(target == null || target == 'Core'){
  var doc = docs[target];
  // console.log(doc);
  if(view_type == 'manual'){
    doc_draw(doc);
  }
  else{}  
}



function doc_draw(doc){
  document.getElementById('doc_breadcrumb').innerHTML = doc.titulo;
  document.getElementById('doc_titulo').innerHTML = doc.titulo;
  document.getElementById('issues_badge').innerHTML = doc.issues.length;
  
  for(i=0;i<doc.topics.length;i++){
    document.getElementById('nav_container').innerHTML += `<li class="text-primary pointer" onclick="goTo('${doc.topics[i].id}');">${doc.topics[i].titulo}</a>`;
    document.getElementById('body_elements_container').innerHTML += doc.topics[i].body;
    
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
// doc_draw(doc);