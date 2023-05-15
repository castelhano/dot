from django.urls import path
from . import views

urlpatterns = [
    path('arquivo_grupos',views.grupos,name='arquivo_grupos'),
    path('arquivo_grupo_add',views.grupo_add,name='arquivo_grupo_add'),
    path('arquivo_grupo_id/<int:id>',views.grupo_id,name='arquivo_grupo_id'),
    path('arquivo_grupo_update/<int:id>',views.grupo_update,name='arquivo_grupo_update'),
    path('arquivo_grupo_delete/<int:id>',views.grupo_delete,name='arquivo_grupo_delete'),
    path('arquivo_containers',views.containers,name='arquivo_containers'),
    path('arquivo_container_add',views.container_add,name='arquivo_container_add'),
    path('arquivo_container_id/<int:id>',views.container_id,name='arquivo_container_id'),
    path('arquivo_container_update/<int:id>',views.container_update,name='arquivo_container_update'),
    path('arquivo_container_delete/<int:id>',views.container_delete,name='arquivo_container_delete'),
    path('arquivo_limites',views.limites,name='arquivo_limites'),
    path('arquivo_limite_add',views.limite_add,name='arquivo_limite_add'),
    path('arquivo_limite_id/<int:id>',views.limite_id,name='arquivo_limite_id'),
    path('arquivo_limite_update/<int:id>',views.limite_update,name='arquivo_limite_update'),
    path('arquivo_limite_delete/<int:id>',views.limite_delete,name='arquivo_limite_delete'),
    path('arquivo_ativos',views.ativos,name='arquivo_ativos'),
    path('arquivo_ativo_add',views.ativo_add,name='arquivo_ativo_add'),
    path('arquivo_ativo_id/<int:id>',views.ativo_id,name='arquivo_ativo_id'),
    path('arquivo_ativo_update/<int:id>',views.ativo_update,name='arquivo_ativo_update'),
    path('arquivo_ativo_delete/<int:id>',views.ativo_delete,name='arquivo_ativo_delete'),
    path('arquivo_get_containers',views.get_containers,name='arquivo_get_containers'),
]