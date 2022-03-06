from django.urls import path
from . import views

urlpatterns = [
    path('globus_escalas',views.escalas,name='globus_escalas'),
    path('globus_escala_add',views.escala_add,name='globus_escala_add'),
    path('globus_escala_id/<int:id>',views.escala_id,name='globus_escala_id'),
    path('globus_escala_update/<int:id>',views.escala_update,name='globus_escala_update'),
    path('globus_escala_delete/<int:id>/delete',views.escala_delete,name='globus_escala_delete'),
    path('globus_escala_importar',views.escala_importar,name='globus_escala_importar'),
]