

from django.http import  HttpResponseBadRequest
from datetime import timezone as dt_timezone


from django.shortcuts import render, redirect
from django.views import View
from app.models import CustomUser, Feedback, ContactForm, ContactNumber, Train, Station, ClassType, Booking, BookingDetail, BillingInfo, Payment, Ticket
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from app.forms import TrainForm
from django.contrib.auth import logout as auth_logout
from datetime import timezone, datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from datetime import datetime  # Make sure you have this
   
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
import requests

from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import MpesaTransaction
import base64

from django.views import View


# Create your views here.
timestamp = datetime.now()

# homepage view

class Home(View):
    def get(self, request):
        form = TrainForm
        return render(request, 'home.html', {'form': form})


from django.shortcuts import get_object_or_404

class AvailableTrain(View):
    def get(self, request):
        if request.GET:
            rfrom = request.GET.get('rfrom')
            to = request.GET.get('to')
            date = request.GET.get('date')
            ctype = request.GET.get('ctype')
            adult = request.GET.get('pa')
            child = request.GET.get('pc')

            try:
                adult = int(adult)
                child = int(child)
            except (ValueError, TypeError):
                messages.warning(request, 'Invalid passenger input')
                return redirect('home')

            if not all([rfrom, to, date, ctype]) or rfrom == 'Select' or to == 'Select' or date in ['mm//dd//yyyy', '']:
                messages.warning(request, 'Please fill up the form properly')
                return redirect('home')

            if (adult + child) < 1:
                messages.warning(request, 'Please book at least 1 seat')
                return redirect('home')

            if (adult + child) > 5:
                messages.warning(request, 'You can book a maximum of 5 seats')
                return redirect('home')

            try:
                source = Station.objects.get(pk=rfrom)
                destination = Station.objects.get(pk=to)
                # Fix: Use get_object_or_404 or check for digit first
                if not ctype.isdigit():
                    messages.warning(request, 'Invalid class type')
                    return redirect('home')
                class_type = ClassType.objects.get(pk=int(ctype))
            except (Station.DoesNotExist, ClassType.DoesNotExist):
                messages.warning(request, 'Invalid station or class type')
                return redirect('home')

            search = Train.objects.filter(
                source=source,
                destination=destination,
                class_type=class_type
            ).distinct()

            context = {
                'search': search,
                'source': source,
                'destination': destination,
                'class_type': class_type,
                'date': date,
                'pa': adult,
                'pc': child,
            }

            return render(request, 'available_train.html', context)

        else:
            messages.warning(request, 'Find a train first to view availability')
            return redirect('home')

#Booking page view
from django.utils import timezone

from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Booking, BookingDetail, BillingInfo, Payment, Ticket, ClassType
from datetime import timedelta
from django.shortcuts import get_object_or_404

class Bookings(View):
    def get(self, request):
        if request.GET:
            user = request.user
            if user.is_authenticated:
                train = request.GET.get('train')
                source = request.GET.get('source')
                destination = request.GET.get('destination')
                date = request.GET.get('date')
                departure = request.GET.get('departure')
                arrival = request.GET.get('arrival')
                tp = request.GET.get('tp')
                pa = request.GET.get('pa')
                pc = request.GET.get('pc')
                ctype = request.GET.get('ctype')
                total_fare = request.GET.get('total_fare')

                fare_each = get_object_or_404(ClassType, pk=ctype)

                ticket = Ticket.objects.filter(train_name=train, travel_date=date)
                available_seat = 30 - ticket.count()

                tp = int(tp)
                if available_seat >= tp:
                    pa = int(pa)
                    pc = int(pc)
                    total_fare = float(total_fare)

                    booking = Booking.objects.create(
                        user=user,
                        source=source,
                        destination=destination,
                        travel_date=date,
                        class_type=fare_each,
                        passengers_adult=pa,
                        passengers_child=pc,
                        train_name=train,
                        departure_time=departure,
                        arrival_time=arrival,
                        total_fare=total_fare
                    )

                    return render(request, 'booking.html', {
                        'booking': booking,
                        'train': train,
                        'source': source,
                        'destination': destination,
                        'date': date,
                        'departure': departure,
                        'arrival': arrival,
                        'tp': tp,
                        'pa': pa,
                        'pc': pc,
                        'ctype': ctype,
                        'total_fare': total_fare,
                        'fare_each': fare_each
                    })
                else:
                    messages.warning(request, f"Sorry! Only {available_seat} seat(s) available. Try again!")
                    return redirect('home')
            else:
                messages.warning(request, "Please login to book a train.")
                return redirect('login')
        else:
            messages.warning(request, 'Find a train first!')
            return redirect('home')



      
from django.shortcuts import render, get_object_or_404
from .models import Booking, ClassType

def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    fare_each = ClassType.objects.get(name=booking.class_type)
    
    context = {
        'booking': booking,
        'user': request.user,
        'train': booking.train_name,
        'source': booking.source,
        'destination': booking.destination,
        'date': booking.date,
        'departure': booking.departure,
        'arrival': booking.arrival,
        'tp': int(booking.passengers_adult) + int(booking.passengers_child),
        'pa': booking.passengers_adult,
        'pc': booking.passengers_child,
        'ctype': booking.class_type,
        'fare_each': fare_each,
        'total_fare': booking.total_price
    }
    return render(request, 'booking.html', context)

# booking history page view

class BookingHistory(View):
    def get(self, request):
        user=request.user
        if user.is_authenticated:
            booking = Booking.objects.filter(user=user).order_by('-id')

            current_time = timezone.now().astimezone(dt_timezone.utc)


            
            return render(request, 'booking_history.html', {'booking':booking, 'current_date':current_time})
        else:
            return redirect('login')

# booking detail page view

class BookingDetails(View):
    def get(self, request, pk):
        user = request.user
        if user.is_authenticated:
            bookings = Booking.objects.get(id=pk)
            if user == bookings.user:
                booking_detail = BookingDetail.objects.get(booking=pk)
                billing = BillingInfo.objects.get(booking=pk)
                payment = Payment.objects.get(booking=pk)
                return render(request, 'booking_detail.html', {'booking_detail':booking_detail, 'billing':billing, 'payment':payment})
            else:
                messages.warning(request, "Invalid booking id!")
                return redirect('booking_history')
        else:
            return redirect('login')


# # ticket page view


class Tickets(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            messages.warning(request, "Please login to view tickets.")
            return redirect('login')

        try:
            booking = get_object_or_404(Booking, id=pk, user=request.user)
            tickets = Ticket.objects.filter(booking=booking)
            print_param = request.GET.get('print', False)
            
            context = {
                'booking': booking,
                'tickets': tickets,
                'print': print_param
            }
            return render(request, 'ticket.html', context)
        except Booking.DoesNotExist:
            messages.warning(request, 'Booking not found or not authorized!')
            return redirect('booking_history')


# cancel booking view

class CancelBooking(View):
    def post(self, request):
        id = request.POST['booking_id']
        Booking.objects.filter(id=id).delete()
        messages.success(request, 'Your booking canceled successfully')
        return redirect(request.META['HTTP_REFERER'])


# signup for user

def signup(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home')
    else:
        if request.method=="POST":
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            email = request.POST['email']
            phone = request.POST['phone']        
            password1 = request.POST['password1']
            password2 = request.POST['password2']

            if password1 != password2:
                messages.warning(request,"Password didn't matched")
                return redirect('signup')
        
            elif username == '':
                messages.warning(request,"Please enter a username")
                return redirect('signup')

            elif first_name == '':
                messages.warning(request,"Please enter first name")
                return redirect('signup')

            elif last_name == '':
                messages.warning(request,"Please enter last name")
                return redirect('signup')

            elif email == '':
                messages.warning(request,"Please enter email address")
                return redirect('signup')

            elif phone == '':
                messages.warning(request,"Please enter phone number")
                return redirect('signup')

            elif password1 == '':
                messages.warning(request,"Please enter password")
                return redirect('signup')

            elif password2 == '':
                messages.warning(request,"Please enter confirm password")
                return redirect('signup')
            
            try:
                if CustomUser.objects.all().get(username=username):
                    messages.warning(request,"username not Available")
                    return redirect('signup')

            except:
                pass
                

            new_user = CustomUser.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, phone=phone, password=password1)
            new_user.is_superuser=False
            new_user.is_staff=False
                
            new_user.save()
            messages.success(request,"Registration Successfull")
            return redirect("login")
        return render(request, 'signup.html')


# login for admin and user

def user_login(request):
    check = request.user
    if check.is_authenticated:
        return redirect('home')
    else:
            
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(username=username,password=password)
            
            if user is not None:
                login(request,user)
                messages.success(request,"successful logged in")
                return redirect('home')
            else:
                messages.warning(request,"Incorrect username or password")
                return redirect('login')

    response = render(request, 'login.html')
    return HttpResponse(response)


# contact page view

class Contact(View):
    def get(self, request):
        contact = ContactNumber.objects.all()
        return render(request, 'contact.html', {'contact': contact})

    def post(self, request):
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        if name == '' or email == '' or message == '':
            messages.warning(request, 'Please fillup all the fields to send message!')
            return redirect('contact')
        
        else:
            form = ContactForm(name=name, email=email, message=message)
            form.save()
            messages.success(request, 'You have successfully sent the message!')  
            return redirect('contact')


# feedback page view

class Feedbacks(View):
    def get(self, request):
        feedback = Feedback.objects.all().order_by('-id')
        return render(request, 'feedback.html', {'feedback': feedback})

    def post(self, request):
        user = request.user
        if user.is_authenticated:
            comment = request.POST['feedback']

            if comment == '':
                messages.warning(request, "please write something first and then submit feedback.")
                return redirect('feedback')
            
            else:
                feedback = Feedback(name=user.first_name + ' ' + user.last_name, feedback=comment)
                feedback.save()
                messages.success(request, 'Thanks for your feedback!')
                return redirect('feedback')

        else:
            messages.warning(request, "Please login first to post feedback.")
            return redirect('feedback')


# verify ticket page view

class VerifyTicket(View):
    def get(self, request):
        trains = Train.objects.all()
        if request.GET:

            train = request.GET.get('train')
            date = request.GET.get('date')
            tid = request.GET.get('tid')

            tid = str(tid)
            date = str(date)

            ticket = None

            try:
                ticket = Ticket.objects.get(id=tid, train_name=train, travel_date=date)
                ticket.id = str(ticket.id)
                ticket.travel_date = str(ticket.travel_date)
                return render(request, 'verify_ticket.html', {'train':trains, 'ticket':ticket})

            except:
                ticket = None
                return render(request, 'verify_ticket.html', {'train':trains, 'ticket':ticket})
            
        else:
            return render(request, 'verify_ticket.html', {'train':trains})

        return render(request, 'verify_ticket.html', {'train':trains})



 
     
from django.views import View
from django.shortcuts import render, redirect
from .forms import ProfileForm

class Profile(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        form = ProfileForm(instance=request.user)
        return render(request, 'profile.html', {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Or show a success message
        return render(request, 'profile.html', {'form': form})
   

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
        print('User logged out')
    else:
        print('User was not logged in')
    
    return render(request, 'logout.html')
           

class CustomPasswordResetView(SuccessMessageMixin, PasswordResetView):
    template_name = 'forgot_password.html'
    email_template_name = 'reset_email.html'
    subject_template_name = 'reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    success_message = "We've emailed you instructions for setting your password."
 
     
     

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    access_token = response.json().get('access_token')
    return access_token

def lipa_na_mpesa_online(phone_number, amount):
    try:
        access_token = get_access_token()
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # ✅ CORRECT

        password = base64.b64encode(
            (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
        ).decode()

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "Northern Express",
            "TransactionDesc": "Payment for Train Booking"
        }

        print("[MPESA REQUEST]:", json.dumps(payload, indent=2))
        response = requests.post(api_url, json=payload, headers=headers)

        try:
            return response.json()
        except ValueError:
            print("[MPESA ERROR]: Non-JSON response:", response.text)
            return {"error": "Invalid MPESA response", "raw": response.text}

    except Exception as e:
        print("[MPESA INIT ERROR]:", e)
        return {"error": str(e)}



from app.models import Booking  # or whatever your model is



from django.shortcuts import render, redirect
from django.contrib import messages

@csrf_exempt







@login_required
def process_payment(request):
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        ptype = request.POST.get('ptype')
        payment_code = request.POST.get('payment_code')

        print(f"[PROCESS PAYMENT] Booking ID: {booking_id}, Payment Type: {ptype}, Payment Code: {payment_code}")

        if not booking_id:
            return JsonResponse({'message': 'Booking ID is missing.'}, status=400)

        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Invalid booking ID or booking does not belong to user.'}, status=400)

        if ptype != 'rocket':
            return JsonResponse({'message': 'Other payment methods not implemented yet.'}, status=400)

        if not payment_code:
            return JsonResponse({'message': 'Payment code is required for MPesa confirmation.'}, status=400)

        try:
            mpesa_transaction = MpesaTransaction.objects.get(
                booking=booking, trx_id=payment_code, result_code='0'
            )
        except MpesaTransaction.DoesNotExist:
            return JsonResponse({'message': 'Invalid or unverified MPesa transaction.'}, status=400)

        payment = booking.payment_set.first()
        if not payment:
            return JsonResponse({'message': 'No payment record found for this booking.'}, status=400)

        payment.trxid = payment_code
        payment.save()

        # ✅ Save the phone number from MPesa
        phone = mpesa_transaction.phone_number
        if phone:
            mpesa_transaction.phone_number= phone
            mpesa_transaction.save()

            # ✅ Optionally store it on user's profile if the user model has a phone field
            user = booking.user
            user = mpesa_transaction.booking.user
            user.phone = phone  # Ensure `phone` field exists on User model
            user.save()
            if not user.phone:
                user.phone = phone
                user.save()

        return JsonResponse({
            'message': 'MPesa payment confirmed successfully.',
            'booking_id': booking.id,
            'receipt': {
        'transaction_id': payment_code,
        'amount': mpesa_transaction.amount,
        'phone': mpesa_transaction.phone_number,
        'date': timestamp
    }
        }, status=200)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)


@login_required



@csrf_exempt
def stk_push(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            raw_phone = data.get('phone')

            # Sanitize phone number to 2547XXXXXXXX format
            if not raw_phone:
                return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)

            phone = raw_phone.strip().replace(' ', '').replace('+', '')

            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif phone.startswith('7'):
                phone = '254' + phone
            elif not phone.startswith('254'):
                return JsonResponse({'status': 'error', 'message': 'Phone number must start with 07, 7 or 254'}, status=400)

            # Final validation
            if not phone.isdigit() or len(phone) != 12:
                return JsonResponse({'status': 'error', 'message': 'Invalid phone number format'}, status=400)

            amount = data.get('amount')
            booking_id = data.get('booking_id')

            if not phone or not amount or not booking_id:
                return JsonResponse({'status': 'error', 'message': 'Missing phone, amount, or booking ID'}, status=400)

            # Format phone number to international
            if phone.startswith('0'):
                phone = '254' + phone[1:]

            # Get booking
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid booking ID'}, status=404)

            # Daraja credentials
            consumer_key = settings.MPESA_CONSUMER_KEY
            consumer_secret = settings.MPESA_CONSUMER_SECRET
            shortcode = settings.MPESA_SHORTCODE
            passkey = settings.MPESA_PASSKEY
            callback_url = settings.MPESA_CALLBACK_URL  # Update with actual public URL

            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = base64.b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode('utf-8')

            # Get access token
            token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            r = requests.get(token_url, auth=(consumer_key, consumer_secret))
            access_token = r.json().get('access_token')

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "BusinessShortCode": shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(float(amount)),
                "PartyA": phone,
                "PartyB": shortcode,
                "PhoneNumber": phone,
                "CallBackURL": callback_url,
                "AccountReference": f"Booking{booking_id}",
                "TransactionDesc": "Train Ticket Payment"
            }

            res = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                headers=headers,
                json=payload
            )

            response_data = res.json()
            print("[STK PUSH RESPONSE]", response_data)

            if response_data.get("ResponseCode") == "0":
                merchant_request_id = response_data.get("MerchantRequestID")
                checkout_request_id = response_data.get("CheckoutRequestID")
                

                # Save STK push request to DB
                MpesaTransaction.objects.create(
                    booking=booking,
                    phone_number=phone,
                    amount=amount,
                    merchant_request_id=merchant_request_id,
                    trx_id=checkout_request_id or merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    result_code='-1',  # You can use -1 to mean 'pending'
                    transaction_date=timezone.now()

                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'STK Push initiated',
                    'response': response_data
                })

            else:
                return JsonResponse({
                    'status': 'error',
                    'message': response_data.get('errorMessage', 'Failed to initiate STK push')
                }, status=400)

        except Exception as e:
            print(f"[STK PUSH ERROR]: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return HttpResponseBadRequest("Invalid request method")


@csrf_exempt
def mpesa_callback(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        body = data.get("Body", {}).get("stkCallback", {})
        merchant_request_id = body.get("MerchantRequestID")
        checkout_request_id = body.get("CheckoutRequestID")
        result_code = str(body.get("ResultCode"))
        result_desc = body.get("ResultDesc")

        trx_id = None
        amount = None
        phone = None

        # Extract transaction details from metadata
        for item in body.get("CallbackMetadata", {}).get("Item", []):
            if item["Name"] == "MpesaReceiptNumber":
                trx_id = item["Value"]
            elif item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone = item["Value"]

        print(f"[CALLBACK] CheckoutRequestID: {checkout_request_id}, TrxID: {trx_id}, ResultCode: {result_code}, Amount: {amount}, Phone: {phone}")

        # Get transaction object
        try:
            mpesa_transaction = MpesaTransaction.objects.get(
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id
            )

            transaction = MpesaTransaction.objects.filter(trx_id=checkout_request_id).first()
            if transaction:
                # transaction.trx_id = actual_mpesa_code  # e.g. "TGP4GUGY5S"
                transaction.result_code = str(result_code)  # 0 = success
                transaction.save()

        except MpesaTransaction.DoesNotExist:
            print(f"[CALLBACK ERROR]: No MpesaTransaction found for CheckoutRequestID: {checkout_request_id}")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Transaction not found"}, status=404)

        # Update transaction record
        mpesa_transaction.trx_id = trx_id
        mpesa_transaction.result_code = result_code
        mpesa_transaction.result_desc = result_desc
        mpesa_transaction.amount = amount
        mpesa_transaction.phone_number = phone  # ensure this matches your model field
        mpesa_transaction.save()

        # Optionally update user's phone number if not already set
        user = mpesa_transaction.booking.user
        if hasattr(user, 'phone') and (not user.phone or user.phone.strip() == ""):
            user.phone = phone
            user.save()

        # Create or update payment record
        if result_code == '0':
            payment, _ = Payment.objects.get_or_create(booking=mpesa_transaction.booking)
            payment.trxid = trx_id
            payment.save()
            print(f"[CALLBACK] Payment saved for Booking ID: {mpesa_transaction.booking.id}, TrxID: {trx_id}")
            amount = result['CallbackMetadata']['Item'][0]['Value']
            mpesa_code = result['CallbackMetadata']['Item'][1]['Value']
            phone = result['CallbackMetadata']['Item'][4]['Value']

            MpesaTransaction.objects.filter(checkout_request_id=checkout_request_id).update(
                trx_id=mpesa_code,
                result_code=result_code,
                result_desc=result_desc,
                phone_number=phone,
                amount=amount
            )

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted",'Result': 'Received'}, status=200)

    except Exception as e:
        print(f"[CALLBACK ERROR]: {e}")
        return JsonResponse({"ResultCode": 1, "ResultDesc": f"Failed: {str(e)}"}, status=500)


class TicketView(View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)
        tickets = Ticket.objects.filter(booking=booking)
        return render(request, 'ticket.html', {
            'booking': booking,
            'tickets': tickets,
            'print': request.GET.get('print', False),
        })
