from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = "ShopHome"),
    path('about/', views.about, name = "AboutUs"),
    path('contact/', views.contact, name = "ContactUs"),
    path('tracker/', views.tracker, name = "TrackingStatus"),
    path('search/', views.search, name = "Search"),
    path('products/<int:myid>', views.productview, name = "ProductView"),
    path('checkout/', views.checkout, name = "CheckOut"),
    path('simple-checkout/', views.simpleCheckout, name = "Simple-checkout"),
    path('complete/', views.paymentComplete, name="complete"),
    path('signup/', views.handleSignUp, name="handleSignUp"),
    path('login/', views.handleLogin, name="handleLogin"),
    path('logout/', views.handleLogout, name="handleLogout"),
    #path('handlerequest/', views.handlerequest, name = "HandleRequest"),



]
