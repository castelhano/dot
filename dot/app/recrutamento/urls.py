from django.urls import path
from . import views

urlpatterns = [
    path('recrutamento_candidatos',views.candidatos,name='recrutamento_candidatos'),
    path('recrutamento_candidato_add',views.candidato_add,name='recrutamento_candidato_add'),
    path('recrutamento_candidato_id/<int:id>',views.candidato_id,name='recrutamento_candidato_id'),
    path('recrutamento_candidato_update/<int:id>',views.candidato_update,name='recrutamento_candidato_update'),
    path('recrutamento_candidato_delete/<int:id>/delete',views.candidato_delete,name='recrutamento_candidato_delete'),
    path('recrutamento_selecoes',views.selecoes,name='recrutamento_selecoes'),
    path('recrutamento_selecao_add',views.selecao_add,name='recrutamento_selecao_add'),
    path('recrutamento_selecao_id/<int:id>',views.selecao_id,name='recrutamento_selecao_id'),
    path('recrutamento_selecao_update/<int:id>',views.selecao_update,name='recrutamento_selecao_update'),
    path('recrutamento_selecao_delete/<int:id>/delete',views.selecao_delete,name='recrutamento_selecao_delete'),
    path('recrutamento_vagas',views.vagas,name='recrutamento_vagas'),
    path('recrutamento_vaga_add',views.vaga_add,name='recrutamento_vaga_add'),
    path('recrutamento_vaga_id/<int:id>',views.vaga_id,name='recrutamento_vaga_id'),
    path('recrutamento_vaga_update/<int:id>',views.vaga_update,name='recrutamento_vaga_update'),
    path('recrutamento_vaga_delete/<int:id>/delete',views.vaga_delete,name='recrutamento_vaga_delete'),
    path('recrutamento_criterios',views.criterios,name='recrutamento_criterios'),
    path('recrutamento_criterio_add',views.criterio_add,name='recrutamento_criterio_add'),
    path('recrutamento_criterio_id/<int:id>',views.criterio_id,name='recrutamento_criterio_id'),
    path('recrutamento_criterio_update/<int:id>',views.criterio_update,name='recrutamento_criterio_update'),
    path('recrutamento_criterio_delete/<int:id>/delete',views.criterio_delete,name='recrutamento_criterio_delete'),
    path('recrutamento_avaliacao_add/<int:selecao_id>',views.avaliacao_add,name='recrutamento_avaliacao_add'),
    path('recrutamento_avaliacao_delete/<int:id>/delete',views.avaliacao_delete,name='recrutamento_avaliacao_delete'),
    path('recrutamento_get_vagas',views.get_vagas,name='recrutamento_get_vagas'),
    path('recrutamento_get_cargos_banco',views.get_cargos_banco,name='recrutamento_get_cargos_banco'),
]