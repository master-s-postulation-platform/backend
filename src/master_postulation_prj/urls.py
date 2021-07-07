# Django
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

# Views
from .views import SignUp, Login

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/v1/', include('djoser.urls')),
    path('api/v1/users/', SignUp.as_view({"post": "create"}), name='signup'),
    path('api/v1/token/login', Login.as_view(), name='login'),
    path('api/v1/', include('djoser.urls.authtoken')),
    path('api/v1/profile/', include('profiles.urls')),
    path('api/v1/administration/', include('administration.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
