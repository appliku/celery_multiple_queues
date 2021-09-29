from collections import namedtuple

CONTACT_UPLOAD_STATUSES = namedtuple(
    'CONTACT_UPLOAD_STATUSES',
    "pending processing finished failed")._make(range(4))
