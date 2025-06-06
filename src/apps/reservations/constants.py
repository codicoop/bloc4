from datetime import time
from decimal import Decimal

from django.utils.translation import gettext_lazy as _

START_TIME = time(8, 0)
START_TIME_PLUS_ONE = time(9, 0)
HALF_TIME = time(13, 0)
END_TIME = time(20, 0)
END_TIME_MINUS_ONE = time(19, 0)
# Discounts
HOSTED_DISCOUNT = Decimal(-0.4)
BLOC4_DISCOUNT = Decimal(-0.5)
GENERAL_DISCOUNT = Decimal(0)
FEDERATED_DISCOUNT = Decimal(-0.3)
OUTSIDE_DISCOUNT = Decimal(0.15)
# Months
MONTHS = {
    1: _("January"),
    2: _("February"),
    3: _("March"),
    4: _("April"),
    5: _("May"),
    6: _("June"),
    7: _("July"),
    8: _("August"),
    9: _("September"),
    10: _("October"),
    11: _("November"),
    12: _("December"),
}
# Percentage. It's NOT saved in the database, only used to calculate the total
# price in the template. Therefore, changing it will modify the VAT amount and
# the total price for all the historical data.
# Without the round, the value becomes:
# 0.2099999999999999922284388276239042170345783233642578125
VAT = round(Decimal(0.21), 2)
