"""Реализация с помощью dateutil"""
import datetime

from dateutil.parser import parse
from dateutil.rrule import rrule, MONTHLY


class Payments:

    def __init__(self, summa, begin, end, current, last=None):
        self.total = summa
        self.begin_contract = self.convert_date(begin)
        self.end_contract = self.convert_date(end)
        self.current_date = self.convert_date(current)
        if last:
            self.last_payment = self.convert_date(last)
        else:
            self.last_payment = self.begin_contract
        self.overdue = {
            'upto30': 0,
            '30-60': 0,
            '60-90': 0,
            'over90': 0
        }

    def convert_date(self, input_date):
        """Конвертация заданной даты в тип datetime.date."""
        return parse(str(input_date)).date()

    def get_days_Contract(self):
        """Общее число дней договора."""
        return (self.end_contract - self.begin_contract).days

    def get_priceDay(self):
        """Цена одного дня договора."""
        return self.total // self.get_days_Contract()

    def get_payments(self):
        """Определяет список дат платежей, включая дату подписания и окончания договора."""
        a = list(map(datetime.datetime.date, rrule(
            freq=MONTHLY,
            dtstart=self.begin_contract,
            until=self.end_contract,
            interval=MONTHLY
        )))
        if a and a[-1] != self.end_contract:
            a.append(self.end_contract)
        return a

    def get_lastRequiredDate(self, input_date):
        """Определяет последнюю дату платежа меньше заданной даты."""
        nearest_list = [i for i in self.get_payments() if i <= input_date]
        nearest_data = min(nearest_list, key=lambda x: abs(x - input_date)) if nearest_list else self.begin_contract
        return nearest_data

    def get_overdueDays(self):
        return (self.get_lastRequiredDate(self.current_date) - self.get_lastRequiredDate(str(self.last_payment))).days

    def get_overdueList(self):
        """Лист пропущенных платежей."""
        a = [i for i in self.get_payments() if self.get_lastRequiredDate(self.last_payment) <= i < self.current_date]
        if len(a) >= 1:
            a = a[1:]
        return a

    def set_overdue(self):
        """Расчет сумм пропущенных платежей."""
        d = self.get_overdueList()
        if len(d) > 4:
            self.overdue['over90'] = (d[-4] - d[0]).days * self.get_priceDay()
        if len(d) > 3:
            self.overdue['60-90'] = (d[-3] - d[-4]).days * self.get_priceDay()
        if len(d) > 2:
            self.overdue['30-60'] = (d[-2] - d[-3]).days * self.get_priceDay()
        if len(d) >= 2:
            self.overdue['upto30'] = (d[-1] - d[-2]).days * self.get_priceDay()

    def get_overdue(self):
        """Получение пропущенных платежей."""
        self.set_overdue()
        return self.overdue

    def get_remaining(self):
        """Определяет оставшуюся сумму платежей."""
        remain = self.total - (self.get_lastRequiredDate(self.last_payment) - self.begin_contract).days * self.get_priceDay()
        return remain

    def __str__(self):
        return 'Договор от {} с датой окончания {}'.format(
            self.begin_contract,
            self.end_contract
        )


if __name__ == '__main__':
    pay = Payments(2239180, '2020-08-05', '2021-10-08', '2021-05-08')
    print(pay)
    print('Количество дней:', pay.get_days_Contract())
    print('Цена дня:', pay.get_priceDay())
    print(pay.get_payments())
    print(pay.get_lastRequiredDate('2021-08-06'))
    print(pay.get_remaining())
    print(pay.get_overdueDays('2021-08-02'))
    print(pay.get_overdueList('2021-08-02'))
    (pay.set_overdue('2021-08-02'))
    print(pay.overdue)