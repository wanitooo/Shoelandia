from django.urls import include, path
from . import views

urlpatterns = [
    path("deliverychoices/", views.deliverychoices, name="deliverychoices"),
    path("basket_update_delivery/", views.basket_update_delivery,
         name="basket_update_delivery"),
    path("delivery_address/", views.delivery_address, name="delivery_address"),
    path("payment_selection/", views.payment_selection, name="payment_selection"),
    path("payment_complete/", views.payment_complete, name="payment_complete"),
    path("payment_successful/", views.payment_successful,
         name="payment_successful"),
    path("CoD/", views.payment_complete_cod,
         name="cash_on_delivery"),

]
