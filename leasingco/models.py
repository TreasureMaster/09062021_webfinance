from leasingco.db import get_db


class BaseModel:

    def __init__(self, data=None, table=None):
        self.__table = table
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.create(data)

    def create(self, data=None):
        self.reset()
        if data is not None:
            data = self.transform(data)
            self.__values = data
            for key, value in data.items():
                self.__dictionary['keys'].append(key)
                self.__dictionary['values'].append(value if value else None)

    def reset(self):
        self.__dictionary = {'keys': [], 'values': []}
        self.__values = {}
        self.__id = None

    def transform(self, data):
        data = dict(data)
        data.pop('submit', None)
        data.pop('csrf_token', None)
        self.__id = data.pop('id', None)
        return data

    def get_row(self):
        d = self.__values.copy()
        d['id'] = self.__id
        return d

    def insert(self, data):
        self.create(data)
        query = "INSERT INTO {} ({}) VALUES ({})".format(
            self.__table,
            ','.join(self.__dictionary['keys']),
            ','.join(['?']*len(self.__dictionary['keys']))
        )
        print(self.__dictionary['values'])
        self.cursor.execute(query, self.__dictionary['values'])
        self.db.commit()

    def update(self, data):
        # Сохраняем данные из формы
        self.create(data)
        self.cursor.execute(f"SELECT id FROM {self.__table} WHERE id={self.__id}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        query = "UPDATE {} SET {} WHERE id={}".format(
            self.__table,
            ','.join(map(lambda k: k+'=?', self.__dictionary['keys'])),
            self.__id
        )
        self.cursor.execute(query, self.__dictionary['values'])
        self.db.commit()

    def delete(self, idx):
        self.cursor.execute(f"SELECT * FROM {self.__table} WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"DELETE {self.__table} WHERE id={idx}")
        self.db.commit()

    def select(self, idx):
        self.cursor.execute(f"SELECT id FROM {self.__table} WHERE id={idx}")
        if not self.cursor.fetchone():
            raise ValueError('id еще не существует')
        self.cursor.execute(f"SELECT * FROM {self.__table} WHERE id={idx}")
        self.create(zip([column[0] for column in self.cursor.description], self.cursor.fetchone()))


class Product(BaseModel):

    def __init__(self, data=None):
        super().__init__(data, 'Product')

    def get_storageTitle(self):
        return '{} {} {} {} {}'.format(
            self.__values['prefix'],
            self.__values['manufacturer'],
            self.__values['model'],
            'VIN' + self.__values['VIN'] if self.__values['VIN'] else '',
            self.__values['description'] if self.__values['description'] else ''
        ).strip()

    def get_contractTitle(self):
        return '{} {} {}'.format(
            self.__values['prefix'],
            self.__values['manufacturer'],
            self.__values['model']
        ).strip()


class Region(BaseModel):

    def __init__(self, data=None):
        super().__init__(data, 'Regions')


class Client(BaseModel):

    def __init__(self, data=None):
        super().__init__(data, 'Clients')

    def get_fullTitle(self):
        self.cursor.execute(f"SELECT Incorporation.kind FROM {self.__table} JOIN Incorporation "
                            f"ON {self.__table}.incorp_id=Incorporation.id WHERE id={self.__id}")
        row = self.cursor.fetchone()[0]
        return '{}, {}'.format(
            self.__values['title'],
            row['kind'],
        ).strip()


class Incorporation(BaseModel):

    def __init__(self, data=None):
        super().__init__(data, 'Incorporation')


class Contract(BaseModel):

    def __init__(self, data=None):
        super().__init__(data, 'Contract')
