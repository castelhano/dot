function carregaAlertas() {
  document.getElementById('offcanvas_body').innerHTML = '';
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if(this.readyState == 4 && this.status == 200){
      if(this.responseText == ''){}
      else{
        let obj = JSON.parse(this.responseText);
        let qtde = 0;
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
          let alerta = `<div id="alert_${item}" class="col-12 ${alert_style} p-3 mb-2"><h6 class="m-0">${titulo}</h6><p class="text-justify mt-2 fs-7">${mensagem}</p><div class="row"><div class="col d-grid">${link}</div><div class="col d-grid">${marcar_lido}</div></div></div>`;
          document.getElementById('offcanvas_body').innerHTML += alerta;
          qtde++;
        }
        if(qtde > 0){
          document.getElementById('messages').classList.remove('d-none');
          document.getElementById('messages').classList.add('d-inline');
          document.getElementById('alertas_badge').innerHTML = qtde;
        }
        else{
          document.getElementById('messages').classList.remove('d-inline');
          document.getElementById('messages').classList.add('d-none');
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