from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('indexsuperuser/',views.indexsuperuser,name='indexsuperuser'),
    path('registersuperuser/',views.registersuperuser,name = 'registersuperuser'),
    path('login/',views.login,name = 'login'),
    path('logout/',views.logout,name = 'logout'),
    path('loginsuperuser/',views.loginsuperuser,name = 'loginsuperuser'),
    path('logoutsuperuser/',views.logoutsuperuser,name = 'logoutsuperuser'),
    path('viewannually/<int:year>/<str:encryptedID>/',views.viewannually,name = 'viewannually'),
    path('viewmonthly/<str:month>/<int:year>/<str:encryptedID>/',views.viewmonthly,name = 'viewmonthly'),
    path('viewalluser/',views.viewalluser,name = 'viewalluser'),
    # path('addbill/',views.addbill,name = 'addbill'),
    path('previousbills/', views.previousbills, name = "previousbills"),
    path('Excel/',views.Excel,name = 'Excel'),
    path('adduserExcel/',views.adduserExcel,name = 'adduserExcel'),
    path('adduser/',views.adduser,name = 'adduser'),
    path('edituser/',views.edituser,name = 'edituser'),
    path('deleteuser/',views.deleteuser,name = 'deleteuser'),
    path('deletebill/',views.deletebill,name = 'deletebill'),
    path('deletesuperuser/',views.deleteSuperUser,name = 'deletesuperuser'),
    path('annually/<str:encryptedID>',views.annually,name = 'annually'),
    path('monthly/<str:encryptedID>',views.monthly,name = 'monthly'),
    path('choose/<str:Employee_ID>/<str:otp>',views.choose,name = 'choose'),
    path('send_otp/<str:Email>/<str:Employee_ID>/',views.send_otp,name = 'send_otp'),
    path('check_otp/<str:otp>/<str:Employee_ID>/',views.check_otp,name = 'check_otp'),

    # reset password ------->
    # path('reset_password/', auth_views.PasswordResetView.as_view(), name = "reset_password"),
    # path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name = "password_reset_done"),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name = "password_reset_confirm"),
    # path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name = "password_reset_complete"),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'), 
]


# Command to clear migrations --->
    # find . -path "/migrations/.py" -not -name "_init_.py" -delete
    # find . -path "/migrations/.pyc"  -delete
    # https://ordinarycoders.com/blog/article/django-password-reset