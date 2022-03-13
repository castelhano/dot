from django.urls import path
from . import views

urlpatterns = [
    path('globus_escalas',views.escalas,name='globus_escalas'),
    path('globus_escala_add',views.escala_add,name='globus_escala_add'),
    path('globus_escala_id/<int:id>',views.escala_id,name='globus_escala_id'),
    path('globus_escala_update/<int:id>',views.escala_update,name='globus_escala_update'),
    path('globus_escala_delete/<int:id>/delete',views.escala_delete,name='globus_escala_delete'),
    path('globus_escala_importar',views.escala_importar,name='globus_escala_importar'),
    path('globus_settings',views.settings,name='globus_settings'),
    path('globus_viagens/<int:id>',views.viagens,name='globus_viagens'),
    path('globus_viagem_add/<int:id>',views.viagem_add,name='globus_viagem_add'),
    path('globus_viagem_id/<int:id>',views.viagem_id,name='globus_viagem_id'),
    path('globus_viagem_update/<int:id>',views.viagem_update,name='globus_viagem_update'),
    path('globus_viagem_delete/<int:id>/delete',views.viagem_delete,name='globus_viagem_delete'),
    path('globus_consultar_escala',views.consultar_escala,name='globus_consultar_escala'),
    path('globus_localizar_escala',views.localizar_escala,name='globus_localizar_escala'),
    path('globus_planejamento_linha',views.planejamento_linha,name='globus_planejamento_linha'),
    path('globus_settings_update/<int:id>',views.settings_update,name='globus_settings_update'),
]