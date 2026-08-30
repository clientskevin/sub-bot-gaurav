import enum


class LogTopicEnum(str, enum.Enum):
    payments = "payments"
    errors = "errors"
    users = "users"
    storage = "storage"
    orders = "orders"
    inquiries = "inquiries"
    jobs = "jobs"


class InviteLinkStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    revoked = "revoked"
