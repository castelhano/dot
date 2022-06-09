from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',include('core.urls')),
    path('',include('pessoal.urls')),
    path('',include('recrutamento.urls')),
    path('',include('oficina.urls')),
    path('',include('trafego.urls')),
    path('',include('sinistro.urls')),
    path('',include('globus.urls')),
    path('',include('gestao.urls')),
    path('',include('sac.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)