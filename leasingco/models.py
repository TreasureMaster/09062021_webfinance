from leasingco.db import get_db

class Product:

    def __init__(self, id=None, category_id=None, prefix=None, manufacturer=None,
                       model=None, VIN=None, description=None, year=None):
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.create(id, category_id, prefix, manufacturer, model, VIN, description, year)

    def create(self, id=None, category_id=None, prefix=None, manufacturer=None,
                     model=None, VIN=None, description=None, year=None):
        self.__values = {
            'id': id,
            'category_id': category_id,
            'prefix': prefix,
            'manufacturer': manufacturer,
            'model': model,
            'VIN': VIN,
            'description': description,
            'year': year
        }

    def get_storageTitle(self):
        return '{} {} {} {} {}'.format(
            self.__values['prefix'],
            self.__values['manufacturer'],
            self.__values['model'],
            'VIN' + self.__values['VIN'] if self.__values['VIN'] else '',
            self.__values['description']
        ).strip()

    def get_row(self):
        return self.__values

    def get_contractTitle(self):
        return '{} {} {}'.format(
            self.__values['prefix'],
            self.__values['manufacturer'],
            self.__values['model']
        ).strip()

    def save_data(self, data):
        for key, value in data.items():
            if key in self.__values:
                print(key, value)
                self.__values[key] = value if value else None

    def insert(self, data):
        self.save_data(data)
        prepare = [
            self.__values['category_id'],
            self.__values['prefix'],
            self.__values['manufacturer'],
            self.__values['model'],
            self.__values['VIN'],
            self.__values['description'],
            self.__values['year']
        ]
        query = ("INSERT INTO Product (category_id, prefix, manufacturer, model, VIN, description, year) "
                 "VALUES (?, ?, ?, ?, ?, ?, ?)")
        self.cursor.execute(query, prepare)
        self.db.commit()

    def update(self, data):
        # Сохраняем данные из формы
        self.save_data(data)
        self.cursor.execute(f"SELECT id FROM Product WHERE id={self.__values['id']}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        prepare = [
            self.__values['category_id'],
            self.__values['prefix'],
            self.__values['manufacturer'],
            self.__values['model'],
            self.__values['VIN'],
            self.__values['description'],
            self.__values['year'],
            self.__values['id']
        ]
        query = ("UPDATE Product SET category_id=?, prefix=?, manufacturer=?, "
                            "model=?, VIN=?, description=?, year=? WHERE id=?")
        # print(query)
        self.cursor.execute(query, prepare)
        self.db.commit()

    def delete(self, idx):
        self.cursor.execute(f"SELECT * FROM Product WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"DELETE Product WHERE id={idx}")
        self.db.commit()

    def select(self, idx):
        self.cursor.execute(f"SELECT id FROM Product WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"SELECT * FROM Product WHERE id={idx}")
        product = [dict(zip([column[0] for column in self.cursor.description], row)) for row in self.cursor.fetchall()][0]
        # print(product[0])
        for key, value in product.items():
            self.__values[key] = value


class Region:

    def __init__(self, idx=None, region=None):
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.create(idx, region)

    def create(self, idx=None, region=None):
        self.__values = {
            'id': idx,
            'region': region,
        }

    def get_row(self):
        return self.__values

    def save_data(self, data):
        for key, value in data.items():
            if key in self.__values:
                print(key, value)
                self.__values[key] = value if value else None

    def insert(self, data):
        self.save_data(data)
        prepare = [
            self.__values['region']
        ]
        query = ("INSERT INTO Regions (region) VALUES (?)")
        self.cursor.execute(query, prepare)
        self.db.commit()

    def update(self, data):
        # Сохраняем данные из формы
        self.save_data(data)
        self.cursor.execute(f"SELECT id FROM Regions WHERE id={self.__values['id']}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        prepare = [
            self.__values['region'],
            self.__values['id']
        ]
        query = ("UPDATE Regions SET region=? WHERE id=?")
        self.cursor.execute(query, prepare)
        self.db.commit()

    def delete(self, idx):
        self.cursor.execute(f"SELECT * FROM Regions WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"DELETE Regions WHERE id={idx}")
        self.db.commit()

    def select(self, idx):
        self.cursor.execute(f"SELECT id FROM Regions WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"SELECT * FROM Regions WHERE id={idx}")
        product = [dict(zip([column[0] for column in self.cursor.description], row)) for row in self.cursor.fetchall()][0]
        for key, value in product.items():
            self.__values[key] = value


class Client:

    def __init__(self, id=None, region_id=None, title=None, INN=None, incorp_id=None):
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.create(id, region_id, title, INN, incorp_id)

    def create(self, id=None, region_id=None, title=None, INN=None, incorp_id=None):
        self.__values = {
            'id': id,
            'region_id': region_id,
            'title': title,
            'INN': INN,
            'incorp_id': incorp_id
        }

    def get_fullTitle(self):
        self.cursor.execute(f"SELECT Incorporation.kind FROM Clients JOIN Incorporation "
                            f"ON Clients.incorp_id=Incorporation.id WHERE id={self.__values['id']}")
        row = self.cursor.fetchone()[0]
        return '{}, {}'.format(
            self.__values['title'],
            row['kind'],
        ).strip()

    def get_row(self):
        return self.__values

    def save_data(self, data):
        for key, value in data.items():
            if key in self.__values:
                print(key, value)
                self.__values[key] = value if value else None

    def insert(self, data):
        self.save_data(data)
        prepare = [
            self.__values['region_id'],
            self.__values['title'],
            self.__values['INN'],
            self.__values['incorp_id'],
        ]
        query = ("INSERT INTO Clients (region_id, title, INN, incorp_id) "
                 "VALUES (?, ?, ?, ?)")
        self.cursor.execute(query, prepare)
        self.db.commit()

    def update(self, data):
        # Сохраняем данные из формы
        self.save_data(data)
        self.cursor.execute(f"SELECT id FROM Clients WHERE id={self.__values['id']}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        prepare = [
            self.__values['region_id'],
            self.__values['title'],
            self.__values['INN'],
            self.__values['incorp_id'],
            self.__values['id']
        ]
        query = ("UPDATE Clients SET region_id=?, title=?, INN=?, incorp_id=? WHERE id=?")
        # print(query)
        self.cursor.execute(query, prepare)
        self.db.commit()

    def delete(self, idx):
        self.cursor.execute(f"SELECT * FROM Clients WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"DELETE Clients WHERE id={idx}")
        self.db.commit()

    def select(self, idx):
        self.cursor.execute(f"SELECT id FROM Clients WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"SELECT * FROM Clients WHERE id={idx}")
        client = [dict(zip([column[0] for column in self.cursor.description], row)) for row in self.cursor.fetchall()][0]
        # print(product[0])
        for key, value in client.items():
            self.__values[key] = value


class Incorporation:

    def __init__(self, idx=None, kind=None):
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.create(idx, kind)

    def create(self, idx=None, kind=None):
        self.__values = {
            'id': idx,
            'kind': kind,
        }

    def get_row(self):
        return self.__values

    def save_data(self, data):
        for key, value in data.items():
            if key in self.__values:
                print(key, value)
                self.__values[key] = value if value else None

    def insert(self, data):
        self.save_data(data)
        prepare = [
            self.__values['kind']
        ]
        query = ("INSERT INTO Incorporation (kind) VALUES (?)")
        self.cursor.execute(query, prepare)
        self.db.commit()

    def update(self, data):
        # Сохраняем данные из формы
        self.save_data(data)
        self.cursor.execute(f"SELECT id FROM Incorporation WHERE id={self.__values['id']}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        prepare = [
            self.__values['kind'],
            self.__values['id']
        ]
        query = ("UPDATE Incorporation SET kind=? WHERE id=?")
        self.cursor.execute(query, prepare)
        self.db.commit()

    def delete(self, idx):
        self.cursor.execute(f"SELECT * FROM Incorporation WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"DELETE Incorporation WHERE id={idx}")
        self.db.commit()

    def select(self, idx):
        self.cursor.execute(f"SELECT id FROM Incorporation WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"SELECT * FROM Incorporation WHERE id={idx}")
        product = [dict(zip([column[0] for column in self.cursor.description], row)) for row in self.cursor.fetchall()][0]
        for key, value in product.items():
            self.__values[key] = value