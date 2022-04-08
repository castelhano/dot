from django.urls import path
from . import views

urlpatterns = [
    path('gestao_dashboard',views.dashboard,name='gestao_dashboard'),
    path('gestao_roadmap',views.roadmap,name='gestao_roadmap'),
    path('gestao_analytics',views.analytics,name='gestao_analytics'),
    path('gestao_indicadores',views.indicadores,name='gestao_indicadores'),
    path('gestao_indicador_add',views.indicador_add,name='gestao_indicador_add'),
    path('gestao_indicador_id/<int:id>',views.indicador_id,name='gestao_indicador_id'),
    path('gestao_indicador_update/<int:id>',views.indicador_update,name='gestao_indicador_update'),
    path('gestao_indicador_delete/<int:id>/delete',views.indicador_delete,name='gestao_indicador_delete'),
    path('gestao_apontamentos',views.apontamentos,name='gestao_apontamentos'),
    path('gestao_apontamento_add',views.apontamento_add,name='gestao_apontamento_add'),
    path('gestao_apontamento_id/<int:id>',views.apontamento_id,name='gestao_apontamento_id'),
    path('gestao_apontamento_update/<int:id>',views.apontamento_update,name='gestao_apontamento_update'),
    path('gestao_apontamento_delete/<int:id>/delete',views.apontamento_delete,name='gestao_apontamento_delete'),
    path('gestao_staffs',views.staffs,name='gestao_staffs'),
    path('gestao_staff_add',views.staff_add,name='gestao_staff_add'),
    path('gestao_staff_id/<int:id>',views.staff_id,name='gestao_staff_id'),
    path('gestao_staff_update/<int:id>',views.staff_update,name='gestao_staff_update'),
    path('gestao_staff_delete/<int:id>/delete',views.staff_delete,name='gestao_staff_delete'),
    path('gestao_diretrizes',views.diretrizes,name='gestao_diretrizes'),
    path('gestao_diretriz_add',views.diretriz_add,name='gestao_diretriz_add'),
    path('gestao_diretriz_id/<int:id>',views.diretriz_id,name='gestao_diretriz_id'),
    path('gestao_diretriz_update/<int:id>',views.diretriz_update,name='gestao_diretriz_update'),
    path('gestao_diretriz_finalizar',views.diretriz_finalizar,name='gestao_diretriz_finalizar'),
    path('gestao_diretriz_reativar/<int:id>',views.diretriz_reativar,name='gestao_diretriz_reativar'),
    path('gestao_diretriz_delete/<int:id>/delete',views.diretriz_delete,name='gestao_diretriz_delete'),
    path('gestao_labels',views.labels,name='gestao_labels'),
    path('gestao_label_add',views.label_add,name='gestao_label_add'),
    path('gestao_label_id/<int:id>',views.label_id,name='gestao_label_id'),
    path('gestao_label_update/<int:id>',views.label_update,name='gestao_label_update'),
    path('gestao_label_delete/<int:id>/delete',views.label_delete,name='gestao_label_delete'),
    path('gestao_analises',views.analises,name='gestao_analises'),
    path('gestao_analise_add',views.analise_add,name='gestao_analise_add'),
    path('gestao_analise_id/<int:id>',views.analise_id,name='gestao_analise_id'),
    path('gestao_analise_update/<int:id>',views.analise_update,name='gestao_analise_update'),
    path('gestao_analise_delete/<int:id>/delete',views.analise_delete,name='gestao_analise_delete'),
    path('gestao_planos_arquivados',views.planos_arquivados,name='gestao_planos_arquivados'),
    path('gestao_plano_add/<int:diretriz>',views.plano_add,name='gestao_plano_add'),
    path('gestao_plano_id/<int:id>',views.plano_id,name='gestao_plano_id'),
    path('gestao_plano_update/<int:id>',views.plano_update,name='gestao_plano_update'),
    path('gestao_plano_movimentar/<int:id>',views.plano_movimentar,name='gestao_plano_movimentar'),
    path('gestao_plano_avaliar',views.plano_avaliar,name='gestao_plano_avaliar'),
    path('gestao_plano_delete/<int:id>/delete',views.plano_delete,name='gestao_plano_delete'),
]