"""master_postulation_prj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
#Django
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from .views import SignUp, Login

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/', include('djoser.urls')),
    path('api/v1/users/', SignUp.as_view({"post":"create"}), name='signup'),
    path('api/v1/token/login', Login.as_view(), name='login'),
    path('api/v1/', include('djoser.urls.authtoken')),
    path('api/v1/profile/', include('profiles.urls')),
    path('api/v1/administration/', include('administration.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
