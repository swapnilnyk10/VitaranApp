from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('indexsuperuser/<str:username>/',views.indexsuperuser,name='indexsuperuser'),
    path('registersuperuser/',views.registersuperuser,name = 'registersuperuser'),
    path('login/',views.login,name = 'login'),
    path('loginsuperuser/',views.loginsuperuser,name = 'loginsuperuser'),
    # path('logoutsuperuser/',views.logoutsuperuser,name = 'logsuperuser'),
    path('viewannually/<int:year>/<str:encryptedID>/',views.viewannually,name = 'viewannually'),
    path('viewmonthly/<str:month>/<int:year>/<str:encryptedID>/',views.viewmonthly,name = 'viewmonthly'),
    path('viewalluser/',views.viewalluser,name = 'viewalluser'),
    path('addbill/',views.addbill,name = 'addbill'),
    path('adduser/',views.adduser,name = 'adduser'),
    path('deleteuser/',views.deleteuser,name = 'deleteuser'),
    path('annually/<str:encryptedID>',views.annually,name = 'annually'),
    path('monthly/<str:encryptedID>',views.monthly,name = 'monthly'),
    path('choose/<str:Employee_ID>',views.choose,name = 'choose'),
    path('send_otp/<str:Email>/<str:Employee_ID>/',views.send_otp,name = 'send_otp'),
    path('check_otp/<str:otp>/<str:Employee_ID>/',views.check_otp,name = 'check_otp'),
]


# Command to clear migrations --->
    # find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    # find . -path "*/migrations/*.pyc"  -delete