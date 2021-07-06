from dateutil.parser import parse
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


class Storage(BaseModel):

    def __init__(self, data=None):
        super().__init__(data, 'Storage')


class PayModel:

    def __init__(self, data=None):
        self.__table = 'Payments'
        self.db = get_db()
        self.cursor = self.db.cursor()
        self.__values = self.create(data)

    def create(self, data=None):
        if data is not None:
            data = list(data)
            years = {d.year for d in data}
            p = {key:{k:None for k in range(1, 13)} for key in years}
            for pay in data:
                p[pay.year][pay.month] = pay
            return p

    def reset(self):
        self.__dictionary = {'keys': [], 'values': []}
        self.__values = {}

    def transform(self, data):
        data = dict(data)
        data.pop('submit', None)
        data.pop('csrf_token', None)
        self.__contract = data.pop('contract_id', None)
        return data

    def get_row(self):
        d = self.__values.copy()
        return d

    def insert(self):
        for year in self.__values:
            for month in self.__values[year]:
                d = (self.__values[year][month])
                if d:
                    print(d)
                    query = "INSERT INTO {} (contract_id, payment_date) VALUES (?,?)".format(
                        self.__table
                    )
                    self.cursor.execute(query, [self.__contract, d])
        self.db.commit()

    def update(self, data):
        # Сохраняем данные из формы
        self.__contract = data['contract']
        print(self.__contract)
        data = map(lambda d: parse(d).date(), data.getlist('date'))
        self.__values = self.create(data)
        self.cursor.execute(f"SELECT id FROM Contract WHERE id={self.__contract}")
        if not self.cursor.fetchone():
            raise ValueError('договора с таким id еще не существует')
        self.cursor.execute(f"SELECT contract_id FROM {self.__table} WHERE contract_id={self.__contract}")
        if not self.cursor.fetchone():
            # просто вставляем
            self.insert()
        else:
            self.__old = self.select(self.__contract, old=True)
            for year in self.__values:
                for month in self.__values[year]:
                    d = (self.__values[year][month])
                    if d:
                        if self.__old.get(year, None) is None or not self.__old.get(year).get(month, None):
                            query = "INSERT INTO {} (contract_id, payment_date) VALUES (?,?)".format(
                                self.__table
                            )
                            self.cursor.execute(query, [self.__contract, d])
            for year in self.__old:
                for month in self.__old[year]:
                    d = (self.__old[year][month])
                    if d:
                        if self.__values.get(year, None) is None or not self.__values.get(year).get(month, None):
                            query = "DELETE {} WHERE contract_id=? AND payment_date=?".format(
                                self.__table
                            )
                            self.cursor.execute(query, [self.__contract, d])
        self.db.commit()

    def select(self, idx, old=False):
        self.__contract = idx
        self.cursor.execute(f"SELECT payment_date FROM {self.__table} WHERE contract_id={idx}")
        pays = map(lambda d: d[0], self.cursor.fetchall())
        if old:
            return self.create(pays)
        else:
            self.__values = self.create(pays)
        