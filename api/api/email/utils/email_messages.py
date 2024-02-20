EMAIL_SIGNATURE = '\n\nThe PREDICO project team'
EMAIL_SUBJECT_FORMAT = '[PREDICO] - '

# Insert here the different components for your email subject and body message

EMAIL_OPTS = {
    'generic-error-email': {
        'subject': EMAIL_SUBJECT_FORMAT + 'An error occurred. Please contact the developers.',
        'message': "{message}"
    },

    'email-bid-confirmation': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Bid confirmation',
        'message': "<p>A bid of <strong>{bid_price}</strong>i "
                   "was successfully registered.<br>"
                   "Some related information about the offer: <br>"
                   "<strong>Resource:</strong> {resource}<br>"
                   "<strong>Session Date:</strong> {session_date}<br>"
                   "<strong>Session Number:</strong> {session_number}<br>"
                   "<strong>Gain function:</strong> {gain_func}<br>"
                   "<strong>Max Payment:</strong> {max_payment}i<br>"
    },

    'email-bid-tangle-id-confirmation': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Tangle Message ID Added to Bid',
        'message': "<p>A tangle message ID was successfully associated "
                   "with your bid for "
                   "resource <strong>{resource}</strong>.<br>"
                   "Some related information about the bid: <br>"
                   "<strong>Resource:</strong> {resource}<br>"
                   "<strong>Session Date:</strong> {session_date}<br>"
                   "<strong>Session Number:</strong> {session_number}<br>"
                   "<strong>Gain function:</strong> {gain_func}<br>"
                   "<strong>Max Payment:</strong> {max_payment}i<br>"
                   "<strong>Tangle Message ID:</strong> {tangle_msg_id}<br>"
    },

    'email-verification': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Email verification',
        'message': '<p>Before using the platform through the API or Website, '
                   'please verify first your email address using '
                   'the button bellow: <br><br></p>'},

    'email-verification-success': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Email verification Success',
        'message': '<p>Your user has been successfully verified! '
                   'Welcome to Predico!</p>'},

    'password-reset-verification': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Password reset verification',
        'message': '<p>Please use the following bellow button to '
                   'reset your password.<br></p>'
                   '<p>If you didn\'t request a password reset you may ignore this email and alert us.</p><br>'},

    'password-reset-success': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Password reset successful',
        'message': '<p>Your password was correctly reset.<br>'
                   'If you didn\'t requested a reset password reply as soon as possible to'
                   ' this email.</p>'},

    'password-change-success': {
        'subject': EMAIL_SUBJECT_FORMAT + 'Password change successful',
        'message': '<p>Your password was correctly changed from the '
                   'Dashboard settings page.<br>'
                   'If you didn\'t requested a password change reply as soon as possible to'
                   ' this email.</p>'},
}
