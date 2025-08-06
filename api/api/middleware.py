import os

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from loguru import logger
from payment.AbstractPayment import AbstractPayment
from payment.PaymentGateway.EthereumPayment.EthereumSmartContract import (
    EthereumSmartContract,
    ethereum_provider,
    SmartContractConfig,
    TokenABI)

from payment.PaymentGateway.IOTAPayment.IOTAPayment import (IOTAPaymentController,
                                                            WalletConfig)
from payment.database.PaymentDatabase import PaymentDatabase as BlockchainDatabase
from payment.database.PaymentDatabase import create_engine, Engine

import threading


class SingletonMeta(type):
    _instances = {}
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


def get_engine() -> Engine:
    db_settings = settings.DATABASES['default']
    db_url = (
        f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@"
        f"{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    )
    return create_engine(db_url)


def smart_contract_config() -> SmartContractConfig:
    return SmartContractConfig(
        contract_address=settings.ERC20_CONTRACT_ADDRESS,
        abi=TokenABI.ETK
    )


class PaymentProcessorSingleton(metaclass=SingletonMeta):
    def __init__(self):
        self.processor = self.initialize_payment_processor()

    def initialize_payment_processor(self) -> AbstractPayment:
        payment_type = settings.PAYMENT_METHOD_PROCESSOR
        try:
            if payment_type == "ERC20":
                config = smart_contract_config()
                provider_url = os.getenv('WEB3_PROVIDER_URL')
                if not provider_url:
                    raise ValueError("WEB3_PROVIDER_URL environment variable not set")
                w3 = ethereum_provider(url=provider_url)
                eth_private_key = os.getenv('ETH_PRIVATE_KEY', None)
                return EthereumSmartContract(config=config,
                                             private_key=eth_private_key,
                                             web3_instance=w3)

            elif payment_type == "FIAT":
                raise NotImplementedError("Fiat exchange processor not yet supported")
            else:
                raise ValueError("Unsupported exchange processor type")
        except Exception as e:
            raise e


def get_payment_processor() -> AbstractPayment:
    return PaymentProcessorSingleton().processor


class PaymentProcessorMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        request.payment_processor = get_payment_processor()

