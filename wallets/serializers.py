from rest_framework.serializers import ModelSerializer, Serializer
from wallets.models import *


class WalletSerializers(ModelSerializer):
    class Meta:
        exclude = []
        model = Wallet
