from django.urls import path
from . import views

urlpatterns = [
    path('sac_classificacoes',views.classificacoes,name='sac_classificacoes'),
    path('sac_classificacao_add',views.classificacao_add,name='sac_classificacao_add'),
    path('sac_classificacao_id/<int:id>',views.classificacao_id,name='sac_classificacao_id'),
    path('sac_classificacao_update/<int:id>',views.classificacao_update,name='sac_classificacao_update'),
    path('sac_classificacao_delete/<int:id>/delete',views.classificacao_delete,name='sac_classificacao_delete'),
    path('sac_reclamacoes',views.reclamacoes,name='sac_reclamacoes'),
    path('sac_reclamacao_add',views.reclamacao_add,name='sac_reclamacao_add'),
    path('sac_reclamacao_id/<int:id>',views.reclamacao_id,name='sac_reclamacao_id'),
    path('sac_reclamacao_update/<int:id>',views.reclamacao_update,name='sac_reclamacao_update'),
    path('sac_reclamacao_delete/<int:id>/delete',views.reclamacao_delete,name='sac_reclamacao_delete'),
    path('sac_settings',views.settings,name='sac_settings'),
    path('recrutamento_settings_update/<int:id>',views.settings_update,name='recrutamento_settings_update'),
    # path('sac',views.reclamacao_site,name='sac_reclamacao_site'),
]