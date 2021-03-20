import pytest
from erddapClient.parse_utils import parseDictMetadata, parseConstraintValue, validate_iso8601, validate_constraint_time_operations, validate_constraint_var_operations


def test_valid_iso8601dates():
    validDates = ["2020-12-24T00:00:00Z", "2020-01-01", "2020-01", "2019-01-11T12"]
    print("Valid dates:")
    for testDate in validDates:
        print (testDate)
        assert validate_iso8601(testDate)

    invalidDates = ["20201224T00:00:00Z", "2020-1-1", "2020/01", "2019-01-11T12;22"]
    print("Invalid dates:")
    for testDate in invalidDates:
        print (testDate)
        assert not validate_iso8601(testDate)

def test_extended_time_constraint_functionality():

    constraintValues = ["max(time)-1months", "min(time)+1years", "min(time)+100seconds", "min(time)+20minutes", 
                        "max(time)-3hours", "max(time)-5days"]
    for testC in constraintValues:
        print (testC)
        assert validate_constraint_time_operations(testC) 

    invalidConstraintValues = ["max(time)*1months", "min(time)+1year", "min(time)+100.50seconds", "min[time]+2minutes", 
                        "max(time)-3hourly", "max(time)-5weeks"]
    for testC in invalidConstraintValues:
        print (testC)
        assert not validate_constraint_time_operations(testC) 

def test_extended_var_constraint_functionality():

    constraintValues = ["max(pressure)-10.5", "min(temperature)+5", "max(salinity)"]
    for testC in constraintValues:
        print (testC)
        assert validate_constraint_var_operations(testC) 

    invalidConstraintValues = ["max(pressure)-10.5.3", "min(temperature)/5.2.3", "max(25+salinity)"]
    for testC in invalidConstraintValues:
        print (testC)
        assert not validate_constraint_var_operations(testC) 

