function carregaAlertas() {
  document.getElementById('offcanvas_body').innerHTML = '';
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200){
      if(this.responseText == ''){}
      else{
        let obj = JSON.parse(this.responseText);
        let qtde = 0;
        let ancor = document.querySelector('[data-type=dotOffcanvasAncor]');
        for(item in obj){
          let titulo = obj[item].fields.titulo;
          let mensagem = obj[item].fields.mensagem;
          let alert_style = obj[item].fields.alert_class_list != '' ? obj[item].fields.alert_class_list : 'bg-dark-alt border border-4 border-oil text-light';
          let action_style = obj[item].fields.action_class_list != '' ? obj[item].fields.action_class_list : 'btn btn-sm btn-secondary opacity-75 rounded-0';
          let link = '';
          if(obj[item].fields.link != ''){
            link = `<a class="${action_style}" href="${obj[item].fields.link}">Link</a>`;
          }
          let marcar_lido = `<a class="${action_style}" onclick="marcarAlertaLido(${obj[item].pk})">Fechar</a>`;
          let pin = obj[item].fields.critico == true ? '<i class="fas fa-thumbtack text-muted ms-auto fs-5" style="position:absolute;top:0px;right:2px;"></i>' : '';
          // let alerta = `<div id="alert_${item}" class="col-12 ${alert_style} p-3 mb-2"><div style="position:relative;"><h6 class="m-0">${titulo}</h6>${pin}</div><p class="text-justify mt-2 fs-7">${mensagem}</p><div class="row"><div class="col d-grid">${link}</div><div class="col d-grid">${marcar_lido}</div></div></div>`;
          // document.getElementById('offcanvas_body').innerHTML += alerta;
          let alerta = document.createElement('div');alerta.id = `alert_${item}`;alerta.classList = `col-12 ${alert_style} p-3 mb-2`;
          alerta.innerHTML = `<div style="position:relative;"><h6 class="m-0">${titulo}</h6>${pin}</div><p class="text-justify mt-2 fs-7">${mensagem}</p><div class="row"><div class="col d-grid">${link}</div><div class="col d-grid">${marcar_lido}</div></div>`
          ancor.before(alerta);
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