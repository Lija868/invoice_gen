# -*- coding: utf-8 -*-
messages = {
    114: "Unable to process the request at this time, please try again later.",
    200: "Ok",
    201: "Created.",
    202: "Account already verified.",
    204: "No Records found",
    205: "Invalid or Expired otp",
    206: "Invalid or Expired link",
    250: "Information does not exist. Might have been already deleted.",
    302: "First name  cannot be null or empty.",
    303: "Last name  cannot be null or empty.",
    304: "Username cannot be null or empty.",
    305: "Password cannot be null or empty.",
    307: "Email cannot be null or empty.",
    308: "User id cannot be null or empty.",
    325: "Invoices cannot be null or empty.",
    311: "Cannot use previous password.Please try with new password.",
    400: "Bad request",
    401: "Unauthorized token",
    403: "Forbidden.",
    404: "Not Found.",
    410: "Token cannot be empty.",
    501: "Invalid User.",
    502: "Inactive User.",
    503: "Login Failed. Username or password is incorrect.",
    504: "Refresh token cannot be empty.",
    505: "Not Refresh Token.",
    506: "Expired or Invalid Token.",
    600: "Validation failed.",
    604: "Email is not valid.",
    617: "Multiple failed login attempts have been detected on your account.  Your account has been temporarily "
    "locked. Please try logging in again after 5 hours.",
    618: "Password doesn't match the criteria.",
    619: "Current Password does not match with previous one.",
    621: "Email is already registered, try another Email.",
    622: "Not allowed",
}


def get_message(code):
    message = messages[code]
    return message
