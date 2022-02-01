from django.urls import path
from . import views

urlpatterns = [
    path('trafego_linhas',views.linhas,name='trafego_linhas'),
    path('trafego_linha_add',views.linha_add,name='trafego_linha_add'),
    path('trafego_linha_id/<int:id>',views.linha_id,name='trafego_linha_id'),
    path('trafego_linha_update/<int:id>',views.linha_update,name='trafego_linha_update'),
    path('trafego_linha_movimentar/<int:id>',views.linha_movimentar,name='trafego_linha_movimentar'),
    path('trafego_linha_delete/<int:id>/delete',views.linha_delete,name='trafego_linha_delete'),
    path('trafego_localidades',views.localidades,name='trafego_localidades'),
    path('trafego_localidade_add',views.localidade_add,name='trafego_localidade_add'),
    path('trafego_localidade_id/<int:id>',views.localidade_id,name='trafego_localidade_id'),
    path('trafego_localidade_update/<int:id>',views.localidade_update,name='trafego_localidade_update'),
    path('trafego_localidade_delete/<int:id>/delete',views.localidade_delete,name='trafego_localidade_delete'),
    path('trafego_planejamentos',views.planejamentos,name='trafego_planejamentos'),
    path('trafego_patamares/<int:id>',views.patamares,name='trafego_patamares'),
    path('trafego_patamar_update',views.patamar_update,name='trafego_patamar_update'),
    path('trafego_get_linha',views.get_linha,name='trafego_get_linha'),
    path('trafego_get_linhas_empresa',views.get_linhas_empresa,name='trafego_get_linhas_empresa'),
]