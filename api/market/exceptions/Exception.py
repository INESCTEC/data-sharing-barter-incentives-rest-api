from rest_framework.exceptions import APIException


class NoMarketSession(APIException):

    def __init__(self, market_session_id):
        super().__init__(self.default_detail.format(market_session_id))
    status_code = 409
    default_detail = "Market session {} does not exist."
    default_code = 'no_market_session'


class SessionNotOpenForBids(APIException):
    def __init__(self, market_session_id):
        super().__init__(self.default_detail.format(market_session_id))
    status_code = 409
    default_detail = "Market session {} is not open for bids."
    default_code = 'session_not_open_for_bids'


class UnfinishedSessions(APIException):
    def __init__(self):
        super().__init__(self.default_detail)
    status_code = 409
    default_detail = "Unable to create new session. " \
                     "There are still unfinished sessions."
    default_code = 'unfinished_sessions'


class MoreThanOneSessionOpen(APIException):
    def __init__(self, session_id):
        super().__init__(self.default_detail.format(session_id))
    status_code = 409
    default_detail = "Unable to update session. " \
                     "Only one session must be open at each time, and " \
                     "session '{}' is still in 'open' state."
    default_code = 'more_than_one_session_open'


class NoBidsDataFound(APIException):

    def __init__(self, tangle_msg_id):
        super().__init__(self.default_detail.format(tangle_msg_id))
    status_code = 409
    default_detail = "There are no bids with tangle message ID: {}."
    default_code = 'no_bids_data_found'


class BidAlreadyExists(APIException):

    def __init__(self, market_session_id, resource_id):
        super().__init__(self.default_detail.format(market_session_id,
                                                    resource_id))
    status_code = 409
    default_detail = "The user already has a placed bid " \
                     "for session ID {} and resource ID {}."
    default_code = 'bid_already_exists'


class BidPaymentNotFound(APIException):

    def __init__(self, tangle_msg_id):
        super().__init__(self.default_detail.format(tangle_msg_id))
    status_code = 409
    default_detail = "No bid payments were found for tangle_msg_id {}."
    default_code = 'bid_payment_not_found'


class DuplicatedTangleMessageId(APIException):

    def __init__(self, tangle_msg_id):
        super().__init__(self.default_detail.format(tangle_msg_id))
    status_code = 409
    default_detail = "Tangle Message ID {} was already used in previous bids."
    default_code = 'duplicated_tangle_message_id'


class TransactionIdWrongSessionException(APIException):

    def __init__(self, transaction_id):
        super().__init__(self.default_detail.format(transaction_id))
    status_code = 409
    default_detail = "Wrong market session declared for Tangle Message ID {}."
    default_code = 'transaction_id_wrong_session'


class NoTangleMessageIdException(APIException):

    def __init__(self, transaction_id):
        super().__init__(self.default_detail.format(transaction_id))
    status_code = 409
    default_detail = "Tangle Message ID {} not found in IOTA Tangle lookup."
    default_code = 'transaction_id_not_in_tangle'


class BidAlreadyWithTangleIdException(APIException):

    def __init__(self, bid_id):
        super().__init__(self.default_detail.format(bid_id))
    status_code = 409
    default_detail = "A Tangle Message ID already exists for bid ID {}."
    default_code = 'bid_already_with_tangle_id'


class NoTransactionForMarketAddressException(APIException):

    def __init__(self, transaction_id):
        super().__init__(self.default_detail.format(transaction_id))
    status_code = 409
    default_detail = "Tangle Message ID {} was not found in market session {}."
    default_code = 'no_transaction_for_market_address'


class TransactionAlreadyValid(APIException):

    def __init__(self, tangle_msg_id):
        super().__init__(self.default_detail.format(tangle_msg_id))
    status_code = 409
    default_detail = "Tangle message ID {} already validated."
    default_code = 'transaction_already_valid'


class DuplicatedTransactionFound(APIException):
    def __init__(self,
                 transaction_type,
                 user_id,
                 resource_id,
                 market_session_id):
        super().__init__(self.default_detail.format(transaction_type,
                                                    user_id,
                                                    resource_id,
                                                    market_session_id))
    status_code = 409
    default_detail = "Transaction of type '{}' already exists for " \
                     "user '{}', resource '{}' and market session '{}'."
    default_code = 'duplicated_transaction_found'


class TransactionBadOperatorSignal(APIException):

    def __init__(self, transaction_type, amount):
        super().__init__(self.default_detail.format(transaction_type, amount))
    status_code = 409
    default_detail = "Bad operator signal for transaction {} - {}."
    default_code = 'transaction_bad_operator_signal'


class BalanceLowerThanZero(APIException):

    def __init__(self, init_balance, withdraw, new_balance):
        super().__init__(self.default_detail.format(new_balance,
                                                    init_balance,
                                                    withdraw))
    status_code = 409
    default_detail = "Final balance lower than zero. ({} = {} - {})."
    default_code = 'balance_lower_than_zero'


class NoMarketAddress(APIException):

    def __init__(self):
        super().__init__(self.default_detail)
    status_code = 409
    default_detail = "Market wallet address not found. Register an address first."
    default_code = 'no_market_address'


class NoMarketFee(APIException):

    def __init__(self):
        super().__init__(self.default_detail)
    status_code = 409
    default_detail = "There isnt a market fee uploaded for that session."
    default_code = 'no_market_fee'


class MarketAddressAlreadyExists(APIException):

    def __init__(self):
        super().__init__(self.default_detail)
    status_code = 409
    default_detail = "A market address was already registered. " \
                     "Use PUT method to update it."
    default_code = 'market_address_already_exists'


class DuplicatedMarketAddress(APIException):

    def __init__(self, address):
        super().__init__(self.default_detail.format(address))
    status_code = 409
    default_detail = "Market address '{}' already exists."
    default_code = 'duplicated_market_address'


class UserWalletAddressNotFound(APIException):

    def __init__(self, user):
        super().__init__(self.default_detail.format(user))
    status_code = 409
    default_detail = "No wallet address found for user '{}'. " \
                     "Please register your address first."
    default_code = 'user_wallet_address_not_found'


class UserResourceNotRegistered(APIException):

    def __init__(self, user, resource_id):
        super().__init__(self.default_detail.format(resource_id, user))
    status_code = 409
    default_detail = "Resource ID {} is not registered to user '{}'."
    default_code = 'user_resource_not_registered'


class UserBidNotRegistered(APIException):

    def __init__(self, user, bid_id):
        super().__init__(self.default_detail.format(bid_id, user))
    status_code = 409
    default_detail = "Bid ID {} is not registered to user '{}'."
    default_code = 'user_bid_not_registered'


class InvalidResourceBid(APIException):

    def __init__(self):
        super().__init__(self.default_detail)
    status_code = 409
    default_detail = "It is only possible to place bids for measurements " \
                     "resources."
    default_code = 'invalid_resource_bid'


class NoForecastResourceBid(APIException):

    def __init__(self):
        super().__init__(self.default_detail)
    status_code = 409
    default_detail = "It is only possible to place bids for resources with " \
                     "'to_forecast' field equal to True."
    default_code = 'no_forecast_resource_bid'


class InvalidIotaAddress(APIException):

    def __init__(self, address):
        super().__init__(self.default_detail.format(address))
    status_code = 409
    default_detail = "Invalid IOTA address ('{}')."
    default_code = 'invalid_iota_address'
