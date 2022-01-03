import csv
from django.http import HttpResponse
from django.shortcuts import redirect
# from django.contrib import messages
from .models import Funcionario

def export_funcionario_csv(request, id):
    f = Funcionario.objects.get(pk=id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="funcionarios.csv"'
    response.write(u'\ufeff'.encode('utf8'))
    
    headers = ["Id","Empresa","Matricula","Nome","Apelido","Nome Social","Cargo","Sexo","Data Nascim","Rg","Rg Emissao","Rg Orgao Expedidor","Cpf","Titulo Eleitor","Titulo Zona","Titulo Secao","Reservista","Cnh","Cnh Categoria","Cnh Primeira Hab","Cnh Emissao","Cnh Validade","Fone1","Fone2","Email","Endereco","Bairro","Cidade","Uf","Estado Civil","Nome Mae","Nome Pai","Regime","Data Admissao","Data Desligamento","Motivo Desligamento","Usuario","Status"]
    data = []
    data.append(f.id)
    data.append(f.empresa.nome)
    data.append(f.matricula)
    data.append(f.nome)
    data.append(f.apelido)
    data.append(f.nome_social)
    data.append(f.cargo.nome if f.cargo else '')
    data.append(f.get_sexo_display())
    data.append(f.data_nascimento.strftime("%d/%m/%Y") if f.data_nascimento else '')
    data.append(f.rg)
    data.append(f.rg_emissao)
    data.append(f.rg_orgao_expedidor)
    data.append(f.cpf)
    data.append(f.titulo_eleitor)
    data.append(f.titulo_zona)
    data.append(f.titulo_secao)
    data.append(f.reservista)
    data.append(f.cnh)
    data.append(f.cnh_categoria)
    data.append(f.cnh_primeira_habilitacao.strftime("%d/%m/%Y") if f.cnh_primeira_habilitacao else '')
    data.append(f.cnh_emissao.strftime("%d/%m/%Y") if f.cnh_emissao else '')
    data.append(f.cnh_validade.strftime("%d/%m/%Y") if f.cnh_validade else '')
    data.append(f.fone1)
    data.append(f.fone2)
    data.append(f.email)
    data.append(f.endereco)
    data.append(f.bairro)
    data.append(f.cidade)
    data.append(f.uf)
    data.append(f.get_estado_civil_display())
    data.append(f.nome_mae)
    data.append(f.nome_pai)
    data.append(f.get_regime_display())
    data.append(f.data_admissao.strftime("%d/%m/%Y") if f.data_admissao else '')
    data.append(f.data_desligamento.strftime("%d/%m/%Y") if f.data_desligamento else '')
    data.append(f.get_motivo_desligamento_display())
    data.append(f.usuario.username if f.usuario else '')
    data.append(f.get_status_display())
    writer = csv.writer(response, delimiter=';')
    writer.writerow(headers)
    writer.writerow(data)
    return response    