from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction, models  # Add models for Q queries
from .models import Transaction, PaymentRequest
from register.models import User
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
# For Currency Exchange
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CurrencyConversionSerializer
from .utils import convert_currency

@login_required
def home(request):
    return render(request, 'payapp/home.html')

@login_required
def transactions(request):
    sent = Transaction.objects.filter(sender=request.user)
    received = Transaction.objects.filter(receiver=request.user)
    requests_sent = PaymentRequest.objects.filter(requester=request.user)
    requests_received = PaymentRequest.objects.filter(target=request.user)

    # Convert amounts
    for req in requests_received:
        if req.status == 'pending':
            req.display_amount, req.display_currency = convert_currency(req.amount, req.requester.currency,
                                                                        request.user.currency)
        else:
            req.display_amount, req.display_currency = req.amount, req.requester.currency

    if request.method == 'POST':
        payment_request_id = request.POST.get('payment_request_id')
        action = request.POST.get('action')

        try:
            payment_request = PaymentRequest.objects.get(id=payment_request_id, target=request.user)
            if action == 'accept':
                with transaction.atomic():
                    # Convert the amount to the target's currency
                    converted_amount, target_currency = convert_currency(payment_request.amount,
                                                                         payment_request.requester.currency,
                                                                         request.user.currency)
                    if request.user.balance >= converted_amount:  # Check if the target has enough money
                        # Deduct converted amount from balanc
                        request.user.balance -= converted_amount
                        # Add amount to requester's balance
                        payment_request.requester.balance += payment_request.amount
                        request.user.save()
                        payment_request.requester.save()
                        payment_request.status = 'accepted'
                        # Record transaction
                        Transaction.objects.create(
                            sender=request.user,
                            receiver=payment_request.requester,
                            amount=payment_request.amount,
                            status='completed'
                        )
                        messages.success(request,
                                         f"Accepted payment request: Sent {converted_amount} {request.user.currency} to {payment_request.requester.username} (they received {payment_request.amount} {payment_request.requester.currency}).")
                    else:
                        messages.error(request, "Insufficient funds to fulfill this request.")
            elif action == 'decline':
                payment_request.status = 'rejected'
                messages.info(request,
                              f"Declined {payment_request.display_amount} {payment_request.display_currency} request from {payment_request.requester.username}.")
            payment_request.save()
        except PaymentRequest.DoesNotExist:
            messages.error(request, "Invalid payment request.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect('payapp:transactions')

    return render(request, 'payapp/transactions.html', {
        'sent': sent,
        'received': received,
        'requests_sent': requests_sent,
        'requests_received': requests_received
    })

@login_required
@transaction.atomic
def make_payment(request):
    if request.method == 'POST':
        receiver_email = request.POST['receiver_email']
        amount = Decimal(request.POST['amount'])

        try:
            receiver = User.objects.get(email=receiver_email)
            if receiver == request.user:
                messages.error(request, "You cannot send money to yourself.")
                return render(request, 'payapp/pay.html')
            if request.user.balance >= amount:
                # Convert the amount to the receiver's currency
                converted_amount, target_currency = convert_currency(amount, request.user.currency, receiver.currency)
                request.user.balance -= amount  # Deduct in sender's currency
                receiver.balance += converted_amount  # Add in receiver's currency
                request.user.save()
                receiver.save()
                Transaction.objects.create(sender=request.user, receiver=receiver, amount=converted_amount)
                messages.success(request,
                                 f"Successfully sent {converted_amount} {receiver.currency} to {receiver.username} (from {amount} {request.user.currency}).")
                return redirect('payapp:transactions')
            else:
                messages.error(request, "Insufficient funds for this transaction.")
        except User.DoesNotExist:
            messages.error(request, "User doesn’t exist with the provided email.")
        except ValueError:
            messages.error(request, "Invalid amount. Please enter a valid number.")

    return render(request, 'payapp/pay.html')

@login_required
def request_payment(request):
    if request.method == 'POST':
        target_email = request.POST['target_email']
        amount = Decimal(request.POST['amount'])

        try:
            target = User.objects.get(email=target_email)
            if target == request.user:
                messages.error(request, "You cannot request money from yourself.")
                return render(request, 'payapp/request.html')
            PaymentRequest.objects.create(requester=request.user, target=target, amount=amount)
            messages.success(request,
                             f"Requested {amount} {request.user.currency} from {target.username}. They will see this as approximately {convert_currency(amount, request.user.currency, target.currency)[0]} {target.currency}.")
            return redirect('payapp:transactions')
        except User.DoesNotExist:
            messages.error(request, "User doesn’t exist with the provided email.")
        except ValueError:
            messages.error(request, "Invalid amount. Please enter a valid number.")

    return render(request, 'payapp/request.html')

class CurrencyConversionView(APIView):
    def post(self, request):
        serializer = CurrencyConversionSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            from_currency = serializer.validated_data['from_currency']
            to_currency = serializer.validated_data['to_currency']

            # Approximate exchange rates
            rates = {
                ('GBP', 'EUR'): Decimal('1.18'),
                ('GBP', 'USD'): Decimal('1.32'),
                ('EUR', 'GBP'): Decimal('0.85'),
                ('EUR', 'USD'): Decimal('1.12'),
                ('USD', 'GBP'): Decimal('0.76'),
                ('USD', 'EUR'): Decimal('0.89'),
            }
            key = (from_currency, to_currency)
            if key in rates:
                converted_amount = amount * rates[key]
                return Response({"converted_amount": str(converted_amount), "currency": to_currency}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Conversion not supported"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def transaction_history(request):
    if request.method == 'POST':
        payment_request_id = request.POST.get('payment_request_id')
        action = request.POST.get('action')

        try:
            payment_request = PaymentRequest.objects.get(id=payment_request_id, target=request.user)
            if action == 'accept':
                with transaction.atomic():
                    # Convert the amount to the target's currency
                    converted_amount, target_currency = convert_currency(payment_request.amount,
                                                                        payment_request.requester.currency,
                                                                        request.user.currency)
                    if request.user.balance >= converted_amount:  # Check if the user has enough money
                        # Deduct amount from balance
                        request.user.balance -= converted_amount
                        # Add amount to requester's balance
                        payment_request.requester.balance += payment_request.amount
                        request.user.save()
                        payment_request.requester.save()
                        payment_request.status = 'accepted'
                        # Record transaction
                        Transaction.objects.create(
                            sender=request.user,
                            receiver=payment_request.requester,
                            amount=payment_request.amount,
                            status='completed'
                        )
                        messages.success(request,
                                        f"Accepted payment request: Sent {converted_amount} {request.user.currency} to {payment_request.requester.username} (they received {payment_request.amount} {payment_request.requester.currency}).")
                    else:
                        messages.error(request, "Insufficient funds to fulfill this request.")
            elif action == 'decline':
                payment_request.status = 'rejected'
                messages.info(request,
                              f"Declined {payment_request.amount} {payment_request.requester.currency} request from {payment_request.requester.username}.")
            payment_request.save()
        except PaymentRequest.DoesNotExist:
            messages.error(request, "Invalid payment request.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect('payapp:transaction_history')

    # Fetch all transactions and requests
    sent_transactions = Transaction.objects.filter(sender=request.user)
    received_transactions = Transaction.objects.filter(receiver=request.user)
    pending_requests = PaymentRequest.objects.filter(
        models.Q(requester=request.user) | models.Q(target=request.user),
        status='pending'
    )

    # Combine into a single list
    combined_transactions = []
    for trans in sent_transactions:
        combined_transactions.append({
            'type': 'Outgoing',
            'timestamp': trans.timestamp,
            'other_party': trans.receiver.username,
            'amount': trans.amount,
            'currency': trans.sender.currency,
            'status': trans.status,
            'is_payment_request': False,
        })
    for trans in received_transactions:
        converted_amount, user_currency = convert_currency(trans.amount, trans.sender.currency, request.user.currency)
        combined_transactions.append({
            'type': 'Incoming',
            'timestamp': trans.timestamp,
            'other_party': trans.sender.username,
            'amount': trans.amount,
            'currency': trans.sender.currency,
            'converted_amount': converted_amount,
            'user_currency': user_currency,
            'status': trans.status,
            'is_payment_request': False,
        })
    for req in pending_requests:
        # Convert the amount
        if req.target == request.user:
            converted_amount, user_currency = convert_currency(req.amount, req.requester.currency, request.user.currency)
        else:
            converted_amount, user_currency = req.amount, req.requester.currency
        combined_transactions.append({
            'type': 'Pending (Request)',
            'timestamp': req.timestamp,
            'other_party': req.requester.username if req.target == request.user else req.target.username,
            'amount': req.amount,
            'currency': req.requester.currency,
            'converted_amount': converted_amount,
            'user_currency': user_currency,
            'status': req.status,
            'is_payment_request': True,
            'payment_request_id': req.id,
            'is_target': req.target == request.user,
        })

    # Sort by timestamp
    combined_transactions.sort(key=lambda x: x['timestamp'], reverse=True)

    # Calculate balance history for today
    today = timezone.now()
    start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate the starting balance
    transactions_before_today = Transaction.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user),
        timestamp__lt=start_of_day
    ).order_by('timestamp')

    # Calculate the balance at the start of the day
    initial_balance = request.user.balance
    for trans in transactions_before_today:
        if trans.sender == request.user:
            # Outgoing
            initial_balance += trans.amount
        elif trans.receiver == request.user:
            # Incoming
            converted_amount, _ = convert_currency(trans.amount, trans.sender.currency, request.user.currency)
            initial_balance -= converted_amount

    # Get all transactions for today
    today_transactions = Transaction.objects.filter(
        models.Q(sender=request.user) | models.Q(receiver=request.user),
        timestamp__gte=start_of_day,
        timestamp__lte=today
    ).order_by('timestamp')

    # Build history
    balance_history = [(start_of_day, float(initial_balance))]
    current_balance = initial_balance
    for trans in today_transactions:
        if trans.sender == request.user:
            # Outgoing
            current_balance -= trans.amount
        elif trans.receiver == request.user:
            # Incoming
            converted_amount, _ = convert_currency(trans.amount, trans.sender.currency, request.user.currency)
            current_balance += converted_amount
        balance_history.append((trans.timestamp, float(current_balance)))

    # graph
    if balance_history:
        balance_timestamps = [entry[0].strftime('%H:%M:%S') for entry in balance_history]
        balance_data = [entry[1] for entry in balance_history]
    else:
        # If no transactions today, show a flat line
        balance_timestamps = [start_of_day.strftime('%H:%M:%S'), today.strftime('%H:%M:%S')]
        balance_data = [float(initial_balance), float(initial_balance)]

    return render(request, 'payapp/transaction_history.html', {
        'combined_transactions': combined_transactions,
        'balance_timestamps': balance_timestamps,
        'balance_data': balance_data,
    })