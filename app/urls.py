

from django.urls import path,include

from .  import views
urlpatterns = [
  
    path('logout/',views.logout , name='logout'),

]
