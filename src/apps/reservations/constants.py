from datetime import time

from django.utils.translation import gettext_lazy as _

START_TIME = time(8, 0)
START_TIME_PLUS_ONE = time(9, 0)
HALF_TIME = time(13, 0)
END_TIME = time(18, 0)
END_TIME_MINUS_ONE = time(17, 0)
# Discounts
GENERAL_DISCOUNT = 0
HOSTED_DISCOUNT = -0.4
BLOC4_DISCOUNT = -0.5
OUTSIDE_DISCOUNT = 0.15
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
