from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(views.search_view), name='search'),

    path('blank1/', login_required(views.blank_page_1), name='blank_page_1'),
    path('blank2/', login_required(views.blank_page_2), name='blank_page_2'),
    path('blank3/', login_required(views.blank_page_3), name='blank_page_3'),
    path('blank4/', login_required(views.blank_page_4), name='blank_page_4'),
    path('blank5/', login_required(views.blank_page_5), name='blank_page_5'),
    path('', views.search_view, name='search_view'),

    # Страница логина/регистрации без login_required
    path('registration/', views.blank_page_6, name='registration'),
    path('take_to_work/', views.take_to_work, name='take_to_work'),
    # Logout с переходом на страницу авторизации
    path('logout/', views.logout_view, name='logout'),
    
    path('blank6/', views.blank_page_6, name='login'),
    path('take_item/', views.take_item, name='take_item'),
    path('take_in_work/', views.take_in_work, name='take_in_work'),
    path('delete_item/', views.delete_item, name='delete_item'),

]
