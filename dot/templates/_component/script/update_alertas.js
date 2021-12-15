function carregaAlertas() {
  document.getElementById('alertas_container').innerHTML = '';
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
          let create_at = obj[item].fields.create_at;
          let style = obj[item].fields.critico == true ? 'bg-danger text-light' : 'bg-light';
          let link = '';
          if(obj[item].fields.link != ''){
            link = obj[item].fields.critico == true ? `<a class="btn btn-sm btn-outline-light" href="${obj[item].fields.link}">Link</a>` : `<a class="btn btn-sm btn-outline-secondary" href="${obj[item].fields.link}">Link</a>`;
          }
          let marcar_lido = obj[item].fields.critico == true ? `<a class="btn btn-sm btn-outline-light" onclick="marcarAlertaLido(${obj[item].pk})">Fechar</a>` : `<a class="btn btn-sm btn-outline-secondary" onclick="marcarAlertaLido(${obj[item].pk})">Fechar</a>`;
          let alerta = `<div id="alert_${item}" class="col-12 ${style} p-3 mb-2 border"><h5 class="m-0">${titulo}</h5><small>${create_at}</small><p class="text-justify mt-2">${mensagem}</p><div class="row"><div class="col d-grid">${link}</div><div class="col d-grid">${marcar_lido}</div></div></div>`;
          document.getElementById('alertas_container').innerHTML += alerta;
          qtde++;
        }
        if(qtde > 0){
          document.getElementById('alertas_badge').classList.remove('d-none');
          document.getElementById('alertas_badge').classList.add('d-inline-block');
          document.getElementById('alertas_badge').innerHTML = qtde;
        }
        else{
          document.getElementById('alertas_badge').classList.remove('d-inline-block');
          document.getElementById('alertas_badge').classList.add('d-none');
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