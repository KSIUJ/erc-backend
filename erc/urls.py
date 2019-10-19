"""erc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from rest_framework import routers

from auth.views import authorize, legacy_lock_controller
from registry.views import MemberViewSet, MembershipViewSet, RoleViewSet, PeriodViewSet, ClientViewSet, \
    AuthEventViewSet
import django_cas_ng.views

router = routers.DefaultRouter()
router.register(r'members', MemberViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'periods', PeriodViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'authevents', AuthEventViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('authorize/', authorize),
    path('lock/authorize', legacy_lock_controller),

    path('admin/', admin.site.urls),

    path('accounts/login/', django_cas_ng.views.LoginView.as_view(),
         name='cas_ng_login'),
    path('accounts/logout/', django_cas_ng.views.LogoutView.as_view(),
         name='cas_ng_logout'),
    path('accounts/callback/', django_cas_ng.views.CallbackView.as_view(),
         name='cas_ng_proxy_callback'),
]
