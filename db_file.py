from Structure import *


import psycopg2

class DataImporter:
    def __init__(self):
        self.postmen = []
        self.clients = []
        self.addresses = []
        self.newspapers = []
        self.postman_newspapers = []
        self.postman_addresses = []
        self.subscriptions = []

    def connect_to_db(self):
        # Подключение к базе данных
        self.conn = psycopg2.connect(
            dbname='PostOffice',
            user='postgres',
            password='Grafin_56',
            host='localhost',
            port='5432'
        )
        self.cur = self.conn.cursor()

    def fetch_data(self):
        self.cur.execute("SELECT id, full_name, phone FROM postmen;")
        postmen_data = self.cur.fetchall()
        for row in postmen_data:
            postman = {'id': row[0],'full_name': row[1],'phone': row[2],'age': 0}
            self.postmen.append(postman)

        self.cur.execute("SELECT id, full_name, phone, address_id FROM clients;")
        clients_data = self.cur.fetchall()
        for row in clients_data:
            client = {
                'id': row[0],
                'full_name': row[1],
                'phone': row[2],
                'age': 0,
                'address_id': row[3]
            }
            self.clients.append(client)

        self.cur.execute("SELECT id, city, street, house_number FROM addresses;")
        addresses_data = self.cur.fetchall()
        for row in addresses_data:
            address = {
                'id': row[0],
                'city': row[1],
                'street': row[2],
                'house_number': row[3]
            }
            self.addresses.append(address)

        # Извлечение данных из таблицы newspapers
        self.cur.execute("SELECT id, name, amount, text FROM newspapers;")
        newspapers_data = self.cur.fetchall()
        for row in newspapers_data:
            newspaper = {
                'id': row[0],
                'name': row[1],
                'amount': row[2],
                'text': row[3]
            }
            self.newspapers.append(newspaper)

        self.cur.execute("SELECT postman_id, newspaper_id FROM postman_newspapers;")
        postman_newspapers_data = self.cur.fetchall()
        for row in postman_newspapers_data:
            self.postman_newspapers.append({'postman_id': row[0], 'newspaper_id': row[1]})

        self.cur.execute("SELECT postman_id, address_id FROM postman_addresses;")
        postman_addresses_data = self.cur.fetchall()
        for row in postman_addresses_data:
            self.postman_addresses.append({'postman_id': row[0], 'address_id': row[1]})

        self.cur.execute("SELECT id, client_id, newspaper_id FROM subscriptions;")
        subscriptions_data = self.cur.fetchall()
        for row in subscriptions_data:
            subscription = {
                'id': row[0],
                'client_id': row[1],
                'newspaper_id': row[2]
            }
            self.subscriptions.append(subscription)

    def close_connection(self):
        self.cur.close()
        self.conn.close()

class DataExporter:
    def __init__(self, clients, postmen, addresses, newspapers):
        self.clients = clients
        self.postmen = postmen
        self.addresses = addresses
        self.newspapers = newspapers

    def connect_to_db(self):
        self.conn = psycopg2.connect(
            dbname='PostOffice',  # Имя вашей базы данных
            user='postgres',  # Ваше имя пользователя
            password='Grafin_56',  # Ваш пароль
            host='localhost',  # Или IP-адрес вашего сервера
            port='5432'  # Порт
        )
        self.cur = self.conn.cursor()

    def clear_database(self):
        self.cur.execute("DELETE FROM postman_newspapers;")
        self.cur.execute("DELETE FROM postman_addresses;")
        self.cur.execute("DELETE FROM subscriptions;")
        self.cur.execute("DELETE FROM clients;")
        self.cur.execute("DELETE FROM newspapers;")
        self.cur.execute("DELETE FROM postmen;")
        self.cur.execute("DELETE FROM addresses;")
        self.conn.commit()

    def insert_addresses(self):
        for address in self.addresses:
            insert_query = "INSERT INTO addresses (city, street, house_number) VALUES (%s, %s, %s) RETURNING id;"
            self.cur.execute(insert_query, (address.GetCity(), address.GetStreet(), address.GetHouseNumber()))
            address.SetId(self.cur.fetchone()[0])
        self.conn.commit()

    def insert_postmen(self):
        for postman in self.postmen:
            insert_query = "INSERT INTO postmen (full_name, phone) VALUES (%s, %s) RETURNING id;"
            self.cur.execute(insert_query, (postman.GetFullName(), postman.GetPhone()))
            postman.SetId(self.cur.fetchone()[0])
        self.conn.commit()

    def insert_newspapers(self):
        for newspaper in self.newspapers:
            insert_query = "INSERT INTO newspapers (name, amount, text) VALUES (%s, %s, %s) RETURNING id;"
            self.cur.execute(insert_query, (newspaper.GetName(), newspaper.GetAmount(), newspaper.GetText()))
            newspaper.SetId(self.cur.fetchone()[0])
        self.conn.commit()

    def insert_clients(self):
        for client in self.clients:
            insert_query = "INSERT INTO clients (full_name, phone, address_id) VALUES (%s, %s, %s) RETURNING id;"
            address_id = client.GetAddress().GetId() if client.GetAddress() else None
            self.cur.execute(insert_query, (client.GetFullName(), client.GetPhone(), address_id))
            client.SetId(self.cur.fetchone()[0])
        self.conn.commit()

    def insert_subscriptions(self):
        for client in self.clients:
            for subscription in client.GetSubscriptions():
                insert_query = "INSERT INTO subscriptions (client_id, newspaper_id) VALUES (%s, %s);"
                self.cur.execute(insert_query, (client.GetId(), subscription.GetId()))
        self.conn.commit()

    def insert_postman_addresses(self):
        for postman in self.postmen:
            for address in postman.GetListOfAddresses():
                insert_query = "INSERT INTO postman_addresses (postman_id, address_id) VALUES (%s, %s);"
                self.cur.execute(insert_query, (postman.GetId(), address.GetId()))
        self.conn.commit()

    def insert_postman_newspapers(self):
        for postman in self.postmen:
            for newspaper in postman.GetListOfNewspapers():
                insert_query = "INSERT INTO postman_newspapers (postman_id, newspaper_id) VALUES (%s, %s);"
                self.cur.execute(insert_query, (postman.GetId(), newspaper.GetId()))
        self.conn.commit()

    def close_connection(self):
        self.cur.close()
        self.conn.close()

data_importer = DataImporter()
data_importer.connect_to_db()
data_importer.fetch_data()
data_importer.close_connection()

print("Postmen:", data_importer.postmen)
print("Clients:", data_importer.clients)
print("Addresses:", data_importer.addresses)
print("Newspapers:", data_importer.newspapers)
print("Postman Newspapers:", data_importer.postman_newspapers)
print("Postman Addresses:", data_importer.postman_addresses)
print("Subscriptions:", data_importer.subscriptions)