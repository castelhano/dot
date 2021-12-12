from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('login',views.login,name='login'),
    path('logout',views.logout,name='logout'),
    path('authenticate',views.authenticate,name='authenticate'),
    path('change_password',views.change_password,name='change_password'),
    path('core_run_script',views.run_script,name='core_run_script'),
    path('logs',views.logs,name='logs'),
    path('handle404',views.handle404,name='handle404'),
    path('handle500',views.handle500,name='handle500'),
    path('core_usuarios',views.usuarios,name='core_usuarios'),
    path('core_empresas',views.empresas,name='core_empresas'),
    path('core_empresa_add',views.empresa_add,name='core_empresa_add'),
    path('core_empresa_id/<int:id>',views.empresa_id,name='core_empresa_id'),
    path('core_empresa_update/<int:id>',views.empresa_update,name='core_empresa_update'),
    path('core_empresa_delete/<int:id>',views.empresa_delete,name='core_empresa_delete'),
    path('core_get_empresas',views.get_empresas,name='core_get_empresas'),
]