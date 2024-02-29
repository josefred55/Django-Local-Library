"""
URL configuration for locallibrary project.

define los mapeos url-vistas. A pesar de que éste podría contener todo el código del mapeo url, es más común delegar algo del mapeo a las propias aplicaciones.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Los mapeos URL se gestionan a través de la variable urlpatterns, que es una lista Python de funciones path(). 
# Cada función path() o asocia un patrón URL a una vista específica, que se presentará cuando el patrón se empareja o 
# con otra lista de código de comprobación de patrones URL (en este segundo caso, los patrones se convierten en la "URL base" de patrones definidos en el módulo destino).

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')), # este path redirige las peticiones con el patrón catalog/ al módulo catalog.urls. algo importante es que django solo envía la parte de la url después del punto que coincide. es decir que al llamar a la función de vista de catalog si la url era /catalog/authors/5 se va a usar /authors/5 porque catalog se asume
    path('', RedirectView.as_view(url='/catalog/', permanent=True)), # esto va a hacer que al visitar la url raiz del proyecto (/) nos redirija a la subdirección de /catalog/ dentro del proyecto para que esta actue como la nueva "url raíz". El primer parametro se deja vacío porque django por defecto sabe que va una "/" por delante
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # habilita el servicio de ficheros estáticos durante el desarrollo (css, javascript, etc)

#Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    # #Add Django site authentication urls (for login, logout, password management). El include es así de específico porque django tiene soporte para casi todo a lo que autenticación se refiere (inicio y cierre de sesión, contraseñas, etc)
    # las vistas que aparecen ahí no son las que vamos a usar, solo estan ahí para que django no tire error de que falta un argumento, las plantillas de vista van a a estar en templates/regitration, no en las carpeta templates de catalog, sino otra afuera de esta
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(),  name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change/done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset/done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
]
