#Local imports
from HelpScripts import *
from ExceptionClass import *


class Person:
    def __init__(self, age, full_name, id, phone):
        NameMask(full_name)
        if isinstance(id, int) and id > 0:
            self.__age = age
            self.__full_name = full_name
            self.__id = id
            self.__phone = PhoneMask(phone)
        else:
            raise ExceptionClass.NotAvailableId
    def __str__(self):
        return f"Person name: {self.__full_name}; age: {self.__age}; his id: {self.__id}; phone: {self.__phone}\n"

    def GetAge(self):
        return self.__age

    def SetAge(self, new_age):
        if isinstance(new_age, int):
            self.__age = new_age
        else:
            raise NotAvailableAge

    def SetFullName(self, new_name):
        NameMask(new_name)
        self.__full_name = new_name

    def GetFullName(self):
        return self.__full_name

    def SetId(self, new_id):
        if isinstance(new_id, int):
            self.__id = new_id
        else:
            raise NotAvailableId

    def GetId(self):
        return self.__id

    def SetPhone(self, new_phone):
        self.__phone = PhoneMask(new_phone)

    def GetPhone(self):
        return self.__phone


class Address:
    def __init__(self, city, street, house_number):
        AddressMask(city)
        AddressMask(street)
        if isinstance(house_number, int) and house_number > 0:
            self.__city = city
            self.__street = street
            self.__house_number = house_number
            self.__id = -1
            self.__client = None
            self.__postman = None
        else:
            raise ExceptionClass.NotAvailableHouseNumber

    def __str__(self):
        return f"Address is: {self.__city}, {self.__street} {self.__house_number}. Client: {self.__client.GetFullName() if self.__client else 'None'}, Postman: {self.__postman.GetFullName() if self.__postman else 'None'}\n"

    def GetFullName(self):
        return f"{self.__city} {self.__street} {self.__house_number}"

    def GetCity(self):
        return self.__city

    def SetCity(self, new_city):
        AddressMask(new_city)
        self.__city = new_city

    def GetStreet(self):
        return self.__street

    def SetStreet(self, new_street):
        AddressMask(new_street)
        self.__street = new_street

    def GetHouseNumber(self):
        return str(self.__house_number)

    def SetHouseNumber(self, new_house_number):
        if isinstance(new_house_number, int) and new_house_number > 0:
            self.__house_number = new_house_number
        else:
            raise ExceptionClass.NotAvailableHouseNumber

    def GetClient(self):
        return self.__client

    def SetClient(self, new_client):
        self.__client = new_client

    def GetPostman(self):
        return self.__postman

    def SetPostman(self, new_postman):
        self.__postman = new_postman

    def SetId(self, new_id):
        if isinstance(new_id, int):
            self.__id = new_id
        else:
            raise NotAvailableId

    def GetId(self):
        return self.__id


class Client(Person):
    def __init__(self, age, full_name, id, phone):
        self.SetAge(age)
        self.SetFullName(full_name)
        self.SetId(id)
        self.SetPhone(phone)
        self.__address = None
        self.__subscriptions = []

    def __str__(self):
        S = super().__str__()
        Subs = " ".join(newspaper.GetName() for newspaper in self.__subscriptions)
        return S + f"   His address: {self.GetAddress().GetCity()} {self.GetAddress().GetStreet()} {self.GetAddress().GetHouseNumber()}\n   Subscriptions: {Subs}\n"

    def GetAddress(self):
        return self.__address

    def SetAddress(self, new_address):
        self.__address = new_address

    def AddSubscription(self, subscription):
        if subscription not in self.__subscriptions:
            self.__subscriptions.append(subscription)

    def SetSubscriptions(self, subscription):
        self.__list_of_newspapers = subscription

    def GetSubscriptions(self):
        return self.__subscriptions[:]


class Postman(Person):
    def __init__(self, age, full_name, id, phone):
        super().__init__(age, full_name, id, phone)
        self.__list_of_addresses = []
        self.__list_of_newspapers = []
        self.__number_of_monthly_deliveries = 0

    def __str__(self):
        S = super().__str__()
        return S + f"   He is postman.\n   Addresses: {len(self.GetListOfAddresses())}\n   Newspapers: {len(self.GetListOfNewspapers())}\n   Monthly deliveries: {self.GetNumberOfMonthlyDeliveries()}\n"

    def AddAddress(self, address):
        self.__list_of_addresses.append(address)

    def GetListOfAddresses(self):
        return self.__list_of_addresses[:]

    def RemoveAddress(self, address):
        if address in self.__list_of_addresses:
            self.__list_of_addresses.remove(address)

    def SetAddresses(self, addresses):
        self.__list_of_addresses = addresses

    def AddNewspaper(self, newspaper):
        if newspaper not in self.__list_of_newspapers:
            self.__list_of_newspapers.append(newspaper)

    def GetListOfNewspapers(self):
        return self.__list_of_newspapers[:]

    def RemoveNewspaper(self, newspaper):
        if newspaper in self.__list_of_newspapers:
            self.__list_of_newspapers.remove(newspaper)

    def SetNewspapers(self, newspapers):
        self.__list_of_newspapers = newspapers

    def SetNumberOfMonthlyDeliveries(self, new_number):
        self.__number_of_monthly_deliveries = new_number

    def GetNumberOfMonthlyDeliveries(self):
        return self.__number_of_monthly_deliveries


class Newspaper:
    def __init__(self, name, amount, text):
        NewspaperNameMask(name)
        NewspaperNameMask(text)
        if isinstance(amount, int) and amount >= 0:
            self.__name = name
            self.__amount = amount
            self.__text = text
            self.__id = -1
        else:
            raise ExceptionClass.NotAvailableAmount

    def __str__(self):
        return f"Читалка -- {self.__name}, amount in storage: {self.__amount}, text: too much\n"

    def SetName(self, new_name):
        NewspaperNameMask(new_name)
        self.__name = new_name

    def GetName(self):
        return self.__name

    def GetFullName(self): #Написано для функции поиска (〜￣▽￣)〜
        return self.__name

    def SetAmount(self, new_amount):
        if isinstance(new_amount, int) and new_amount >= 0:
            self.__amount = new_amount
        else:
            raise ExceptionClass.NotAvailableAmount

    def GetAmount(self):
        return self.__amount

    def SetText(self, new_text):
        NewspaperNameMask(new_text)
        self.__text = new_text

    def GetText(self):
        return self.__text

    def SetId(self, new_id):
        if isinstance(new_id, int):
            self.__id = new_id
        else:
            raise NotAvailableId

    def GetId(self):
        return self.__id