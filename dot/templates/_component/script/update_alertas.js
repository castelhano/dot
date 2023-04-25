function carregaAlertas() {
  document.getElementById('offcanvas_body').innerHTML = '';
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200){
      if(this.responseText == '[]'){document.getElementById('offcanvas_body').innerHTML = '<p class="mb-2 ps-2">Não há novas notificações</p>'}
      else{
        let obj = JSON.parse(this.responseText);
        let qtde = 0;
        for(item in obj){
          let titulo = obj[item].fields.titulo;
          let mensagem = obj[item].fields.mensagem;
          let alert_style = obj[item].fields.alert_class_list != '' ? obj[item].fields.alert_class_list : 'alert alert-dark alert-dismissible mb-1 pb-2';
          let link_style = obj[item].fields.action_class_list != '' ? obj[item].fields.action_class_list : 'fs-7';
          let link = '';
          if(obj[item].fields.link != ''){
            link = `<a class="${link_style} d-inline-block" href="${obj[item].fields.link}" target="_blank">Detalhes</a>`;
          }
          let marcar_lido = `<button class="btn-close" data-bs-dismiss="alert" role="button" onclick="marcarAlertaLido(${obj[item].pk})"></button>`;
          let pin = obj[item].fields.critico == true ? '<sup><i class="fas fa-thumbtack text-body-tertiary ms-2 fs-7"></i></sup>' : '';
          let alerta = document.createElement('div');alerta.classList = `${alert_style}`;
          alerta.innerHTML = `<h6 class="m-0 mb-1">${titulo}${pin}</h6></div><div class="fs-7">${mensagem}</div>${link}${marcar_lido}</div>`
          document.getElementById('offcanvas_body').appendChild(alerta);
          qtde++;
        }
        if(qtde > 0){
          document.getElementById('messages_widget').classList.remove('d-none');
          document.getElementById('messages_widget').classList.add('d-inline');
          document.getElementById('alertas_badge').innerHTML = qtde;
        }
        else{
          document.getElementById('messages_widget').classList.remove('d-inline');
          document.getElementById('messages_widget').classList.add('d-none');
          document.getElementById('alertas_badge').innerHTML = '';            
        }
      }
    }
  };
  xhttp.open("GET", "{% url 'core_get_alertas' %}", true);
  xhttp.send();
}
carregaAlertas();

function marcarAlertaLido(id) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200){carregaAlertas();}
  };
  xhttp.open("GET", "{% url 'core_alerta_marcar_lido' %}?id=" + id, true);
  xhttp.send();
}