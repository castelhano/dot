/******************************************************************************************
* Operações do modelo de dados DOCS
* Author: Rafael Gustavo F Alves [castelhano.rafael@gmail.com]
* Version: 1.00
*******************************************************************************************/

function Tag(nome, url='', classlist='badge bg-primary text-light'){this.nome = nome;this.url = url;this.class_list = classlist;};

function HtmlEL(el, innerHTML='', classlist='', auto_closed_tag=false){
  this.el = el;
  this.attr = [];
  this.auto_closed_tag = auto_closed_tag;
  this.class_list = classlist;
  this.innerHTML = innerHTML;
  this.html = function(){
    if(!this.auto_closed_tag){
      return `<${this.el} class="${this.class_list}">${this.innerHTML}</${this.el}>`;
    }
    else{
      return `<${this.el} class="${this.class_list}" />`;
      
    }
  };
};

function Topic(id, titulo){
  this.id = id;
  this.titulo = titulo;
  this.htmlEls = [];
  this.subtopics = [];
  this.body = '';
  this.add_el = function(e){this.htmlEls.push(e);}
  this.body_print = function(b){this.body += b;}
};

function User(nome, nickname, email=''){
  this.nome = nome;
  this.nickname = nickname;
  this.email = email;
  this.email_href = function(titulo, mensagem){return `mailto:${this.email}?subject=${titulo}&body=${mensagem}`;}
};

function Issue(titulo, descricao, solucao, data_entrada, usuario_entrada, data_conclusao, responsavel_conclusao, status, fechado){
  this.titulo = titulo;
  this.descricao = descricao;
  this.solucao = solucao;
  this.data_entrada = data_entrada;
  this.usuario_entrada = usuario_entrada;
  this.data_conclusao = data_conclusao;
  this.responsavel_conclusao = responsavel_conclusao;
  this.status = status;
  this.fechado = fechado;
  this.href = function(){if(this.url =! ''){window.location = 'url';}else{return false;}};
};

function Docs(){
    this.titulo = '';
    this.tags = [];
    this.topics = [];
    this.issues = [];
};