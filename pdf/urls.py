from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
   
    path("",views.home,name="home"),
    path("merger/",views.merger,name="merger"),
    path("split",views.split,name="split"),
    path("watermark",views.watermark,name="watermark"),
    path("compress",views.compress,name="compress"),
    path("signup",views.signup,name="signup"),
    path("login",views.handlelogin,name="login"),
    path("logout",views.handlelogout,name="logout")
    
]