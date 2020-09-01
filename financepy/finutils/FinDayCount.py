##############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
##############################################################################

from .FinDate import FinDate, monthDaysLeapYear, monthDaysNotLeapYear, datediff
from .FinDate import isLeapYear
from .FinError import FinError
from enum import Enum

# A useful source for these definitions can be found at
# https://developers.opengamma.com/quantitative-research/Interest-Rate-Instruments-and-Market-Conventions.pdf
# and https://en.wikipedia.org/wiki/Day_count_convention
# http://www.fairmat.com/documentation/usermanual/topics/download/mediawiki/index.php/Day_Count_Conventions.htm
# http://www.eclipsesoftware.biz/DayCountConventions.html

###############################################################################


class FinDayCountTypes(Enum):
    THIRTY_E_360_ISDA = 1  # AKA 30E/360 ISDA, EUROBOND (ISDA 2010)
    THIRTY_E_360_PLUS_ISDA = 2  # NEEDS SOURCE
    ACT_ACT_ISDA = 3  # DOES LEAP YEAR SPLIT
    ACT_ACT_ICMA = 4  # DOES LEAP YEAR SPLIT
    ACT_365_ISDA = 5  # SPLITS ACROSS LEAP YEAR
    THIRTY_360 = 6
    THIRTY_360_BOND = 7
    THIRTY_E_360 = 8  # AKA 30/360 ICMA, EUROBOND (ISDA 2006)
    ACT_360 = 9
    ACT_365_FIXED = 10
    ACT_365_LEAP = 11

###############################################################################


class FinDayCount(object):
    ''' Calculate the fractional day count between two dates according to a
    specified day count convention. '''

    def __init__(self,
                 dccType: FinDayCountTypes):
        ''' Create Day Count convention by passing in the Day Count Type. '''

        if dccType not in FinDayCountTypes:
            raise FinError("Need to pass FinDayCountType")

        self._type = dccType

###############################################################################

    def yearFrac(self,
                 dt1: FinDate,
                 dt2: FinDate,
                 dt3: FinDate = None):
        ''' Calculate the year fraction between dates dt1 and dt2 using the
        specified day count convention. '''

        d1 = dt1._d
        d2 = dt2._d
        m1 = dt1._m
        m2 = dt2._m
        y1 = dt1._y
        y2 = dt2._y

        num = 0
        den = 0

        if self._type == FinDayCountTypes.THIRTY_360:

            num = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            den = 360
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.THIRTY_360_BOND:

            d1 = min(d1, 30)

            if d1 == 31 or d1 == 30:
                d2 = min(d2, 30)

            num = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            den = 360
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.THIRTY_E_360:

            d1 = min(d1, 30)
            d2 = min(d2, 30)
            num = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            den = 360
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.THIRTY_E_360_ISDA:

            if isLeapYear(y1):
                if d1 == monthDaysLeapYear[m1 - 1]:
                    d1 = 30

            if isLeapYear(y1) is False:
                if d1 == monthDaysNotLeapYear[m1 - 1]:
                    d1 = 30

            if isLeapYear(y2):
                if d2 == monthDaysLeapYear[m2 - 1] and m2 != 2:
                    d2 = 30

            if isLeapYear(y2) is False:
                if d2 == monthDaysNotLeapYear[m2 - 1] and m2 != 2:
                    d2 = 30

            # Need to exclude termination date - to check this

            num = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            den = 360
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.THIRTY_E_360_PLUS_ISDA:

            # CHECK THIS CODE
            d1 = min(d1, 30)

            if d2 == 31:
                d2 = 1
                m2 = m2 + 1

            num = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
            den = 360
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.ACT_ACT_ISDA:

            if isLeapYear(y1):
                denom1 = 366
            else:
                denom1 = 365

            if isLeapYear(y2):
                denom2 = 366
            else:
                denom2 = 365

            if y1 == y2:
                num = dt2 - dt1
                den = denom1
                accFactor = (dt2 - dt1) / denom1
                return (accFactor, num, den)
            else:
                daysYear1 = datediff(dt1, FinDate(1, 1, y1+1))
                daysYear2 = datediff(FinDate(1, 1, y2), dt2)
                accFactor1 = daysYear1 / denom1
                accFactor2 = daysYear2 / denom2
                yearDiff = y2 - y1 - 1.0
                # I do realise that num/den does not equal accFactor - just need to pass some info back
                num = daysYear1 + daysYear2
                den = denom1 + denom2
                accFactor = accFactor1 + accFactor2 + yearDiff
                return (accFactor, num, den)

        elif self._type == FinDayCountTypes.ACT_ACT_ICMA:

            if dt3 is None:
                raise FinError("ACT_ACT_ICMA requires three dates")

            num = dt2 - dt1
            den = dt3 - dt1
            accFactor = num/den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.ACT_360:

            num = dt2 - dt1
            den = 360
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.ACT_365_FIXED:

            num = dt2 - dt1
            den = 365
            accFactor = num / den
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.ACT_365_LEAP:

            # The ISDA calculator sheet appears to split this across the
            # non-leap and the leap year which I do not see in any conventions.

            denom = 365

            if isLeapYear(y1) and dt1 <= FinDate(28, 2, y1) \
                    and dt2 > FinDate(28, 2, y1):
                denom = 366

            if isLeapYear(y2) and dt1 <= FinDate(28, 2, y2) \
                    and dt2 > FinDate(28, 2, y2):
                denom = 366

            # handle case in which period straddles year end
            num = dt2 - dt1
            accFactor = num / denom
            return (accFactor, num, den)

        elif self._type == FinDayCountTypes.ACT_365_ISDA:

            if isLeapYear(y1):
                denom1 = 366
            else:
                denom1 = 365

            if isLeapYear(y2):
                denom2 = 366
            else:
                denom2 = 365

            if y1 == y2:
                num = dt2 - dt1
                den = denom1
                accFactor = num / denom1
                return (accFactor, num, den)
            else:
                daysYear1 = FinDate(1, 1, y1 + 1) - dt1
                daysYear2 = dt2 - FinDate(1, 1, y1 + 1)

                # I realise that num/den is not equal to accFactor. Just want to pass back some info.
                num = daysYear1 + daysYear2
                den = denom1 + denom2
                accFactor = daysYear1 / denom1
                accFactor += daysYear2 / denom2
                return (accFactor, num, den)
        else:
            raise FinError(str(self._type) +
                           " is not one of FinDayCountTypes")

###############################################################################

    def __repr__(self):
        ''' Returns the calendar type as a string. '''
        return str(self._type)

###############################################################################
