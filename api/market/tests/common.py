from django.urls import reverse
from django.contrib.auth import get_user_model

from ..views.market_wallet import MarketWalletAddress


def drop_dict_field(d, key):
    new_d = d.copy()
    new_d.pop(key)
    return new_d


def create_user(use_custom_data=False, verify_email=True, **kwargs):
    if use_custom_data:
        data = {
            'email': kwargs["email"],
            'password': kwargs["password"],
            'first_name': kwargs["first_name"],
            'last_name': kwargs["last_name"],
        }
    else:
        data = {
            'email': 'carl.sagan@bob.bob',
            'password': 'foo',
            'first_name': "Carl",
            'last_name': "Sagan"
        }

    user = get_user_model().objects.create_user(**data,
                                                is_active=verify_email,
                                                is_verified=verify_email)
    user.raw_password = data["password"]
    return user


def create_superuser():
    data = {'email': 'admin@user.com', 'password': 'admin_foo'}
    admin_user = get_user_model().objects.create_superuser(
        email=data["email"],
        password=data["password"]
    )
    admin_user.raw_password = data["password"]
    return admin_user


def create_and_login_superuser(client):
    user = create_superuser()
    client.login(email=user.email, password=user.raw_password)
    return user


def login_user(client, user):
    response = client.post(reverse("token_obtain_pair"),
                           data={"email": user.email,
                                 "password": user.raw_password})
    user_token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION="Bearer " + user_token)


def create_market_wallet_address():
    address = "atoi1qpx2srs3nw08yuwtyrhsksku5yfkld2fmmmj643nwq4cqyu5xtgfjhh46sp"
    wallet_address = MarketWalletAddress.objects.create(
        wallet_address=address
    )
    return wallet_address


def create_market_session_data(session_number=1):
    return {
        "session_number": session_number,
        "market_price": 56842.10,
        "b_min": 10000.0,
        "b_max": 100000.0,
        "n_price_steps": 20,
        "delta": 0.05
    }


def create_market_bid_data(resource, market_session=1, tangle_msg_id="c3a953db074113291020b39eeb20d116833f31f590b533e967efb247100bd674"):
    return {
        "max_payment": 1000000,
        "bid_price": 1000,
        "resource": resource,
        "market_session": market_session,
        "gain_func": "mse",
        "tangle_msg_id": tangle_msg_id
    }


def create_market_session_weights_data(market_session=1):
    return {
        "weights_p": [20.2, 29.2],
        "market_session": market_session
    }


def create_market_session_fee_data(market_session=1):
    return {
        "market_session": market_session,
        "amount": 500000
    }
