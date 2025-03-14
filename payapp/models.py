from django.db import models
from register.models import User

class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('pending', 'Pending'), ('rejected', 'Rejected')], default='completed')

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.amount}"

class PaymentRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_requests_sent')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_requests_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def __str__(self):
        return f"{self.requester} requests {self.amount} from {self.target}"