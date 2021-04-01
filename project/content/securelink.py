import base64
import hashlib
import calendar
import datetime


def securepath(url):
    secret = "JxSBn5bmqFNJFY5Y2wuqSYoQRBlPZISE"
    # url = "/fullimg/adiraallure/2020-06-15_2316x3088_6fe40ce12e7b0d43e82c5a5c3f14eaa4.jpg"

    future = datetime.datetime.utcnow() + datetime.timedelta(minutes=25)
    expiry = calendar.timegm(future.timetuple())

    secure_link = f"{secret}{url}{expiry}".encode('utf-8')

    hash = hashlib.md5(secure_link).digest()
    base64_hash = base64.urlsafe_b64encode(hash)
    str_hash = base64_hash.decode('utf-8').rstrip('=')
    securedpath = f"{url}?st={str_hash}&e={expiry}"
    return securedpath
