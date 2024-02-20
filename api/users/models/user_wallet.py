from django.db import models
from .user import User


class UserWalletAddress(models.Model):
    # User ID:
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                primary_key=True)
    # User wallet address:
    wallet_address = models.TextField(unique=True, null=False)
    # Register date:
    registered_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'{self.user}'

    class Meta:
        db_table = 'user_wallet_address'
