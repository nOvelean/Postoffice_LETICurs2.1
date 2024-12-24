#local imports
import ExceptionClass

#Global imports
import re


banlistName = "1234567890-_=+!@#$%^&*()№;:?|" + '"' + "'"
banlistAddress = "_=+!@#$%^&*()№;:?|" + '"' + "'"


def NameMask(str):
    for letter in str:
        if letter in banlistName:
            raise ExceptionClass.NotAvailableName
def NewspaperNameMask(str):
    for letter in str:
        if letter in banlistAddress:
            raise ExceptionClass.NotAvailableName
def AddressMask(str):
    for letter in str:
        if letter in banlistAddress:
            raise ExceptionClass.NotAvailableName
def StatusCheck(value):
    if (value > 2) or (value < 0):
        raise ExceptionClass.NotAvailableStatus

def PhoneMask(phone_number):
    digits = re.sub(r'\D', '', phone_number)
    # Проверяем, что номер состоит из 10 цифр (для формата +1(555)555-5555)
    if len(digits) != 10:
        raise ExceptionClass.NotAvailablePhone
    formatted_number = f"{digits[:3]}{digits[3:6]}{digits[6:]}"
    return formatted_number

def SearchbyName(value, arr):
    for str in arr:
        if str.GetFullName().find(value) != -1:
            return str
def SearchbyId(value, arr):
    for item in arr:
        if item.GetId() == value:
            return item