
from django.contrib import admin
from django.urls import path,include
from app.views import confirm_booking,Home, AvailableTrain,stk_push,mpesa_callback, user_login, signup,process_payment,Contact, Feedbacks, Profile, CustomPasswordResetView, Bookings, BookingHistory, BookingDetails, Tickets, CancelBooking, VerifyTicket,logout
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from app.views import (
    Home, AvailableTrain, Bookings, confirm_booking, BookingHistory,
    BookingDetails, Tickets, CancelBooking, signup, user_login, logout,
    Contact, Feedbacks, VerifyTicket, Profile, CustomPasswordResetView,
    process_payment, stk_push, mpesa_callback
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name="home"),
    path('available_train', AvailableTrain.as_view(), name="available_train"),
    path('booking', Bookings.as_view(), name='booking'),
    path('booking_history', BookingHistory.as_view(), name="booking_history"),
    path('booking_history/booking_detail/<int:pk>', BookingDetails.as_view(), name="booking_detail"),
     path('stk-push/', stk_push, name='stk_push'),
    # path('booking_history/ticket/<int:pk>', Tickets.as_view(), name="tickets"),
    # # urls.py
    path('tickets/<int:pk>/', Tickets.as_view(), name='ticket'),
path('confirm-booking/<int:booking_id>/', confirm_booking, name='confirm_booking'),


    path('cancel_booking', CancelBooking.as_view(), name="cancel_booking"),
    path('process-payment/', process_payment, name='process_payment'),
    path('stk-push/', stk_push, name='stk_push'),
    
    path('api/mpesa/callback/', mpesa_callback, name='mpesa_callback'),

    path('contact', Contact.as_view(), name="contact"),
    path('feedback', Feedbacks.as_view(), name="feedback"),
    path('verify_ticket', VerifyTicket.as_view(), name="verify_ticket"),
    path('profile', Profile.as_view(), name="profile"),
    path('login', user_login, name="login"),
    path('signup',signup, name="signup"),
    path('logout',logout , name='logout'),
#    path('logout', auth_views.LogoutView.as_view(), name='logout'),


#   path('app/', include('app.urls')),

 path('forgot-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_complete.html'), name='password_reset_complete'),




] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



#


from django.urls import path
from app.views import (
    Home, AvailableTrain, Bookings, confirm_booking, BookingHistory,
    BookingDetails, Tickets, CancelBooking, signup, user_login, logout,
    Contact, Feedbacks, VerifyTicket, Profile, CustomPasswordResetView,
    process_payment, stk_push, mpesa_callback
)

urlpatterns = [
     path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('available_train/', AvailableTrain.as_view(), name='available_train'),
    path('booking/', Bookings.as_view(), name='booking'),
    path('confirm_booking/<int:booking_id>/', confirm_booking, name='confirm_booking'),
    path('booking_history/', BookingHistory.as_view(), name='booking_history'),
    path('booking_detail/<int:pk>/', BookingDetails.as_view(), name='booking_detail'),
    path('tickets/<int:pk>/', Tickets.as_view(), name='tickets'),
    path('cancel_booking/', CancelBooking.as_view(), name='cancel_booking'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', logout, name='logout'),
    path('contact/', Contact.as_view(), name='contact'),
    path('feedback/', Feedbacks.as_view(), name='feedback'),
    path('verify_ticket/', VerifyTicket.as_view(), name='verify_ticket'),
    path('profile/', Profile.as_view(), name='profile'),
    path('forgot_password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('process_payment/', process_payment, name='process_payment'),
    path('stk_push/', stk_push, name='stk_push'),
    path('mpesa_callback/', mpesa_callback, name='mpesa_callback'),
]




