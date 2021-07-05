from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, IntegerField, SelectField, DateField, FloatField, RadioField)
from wtforms.fields.simple import HiddenField
from wtforms.validators import Email, InputRequired
# from leasingco.custom_validators import AnyInputRequired, Phone


# TODO как отправить данные Flask в форму
# class NameForm(FlaskForm):
#     # 1-й параметр - метка label
#     # 4-й параметр - описание description (под полем формы)
#     # 5-й параметр - идентификатор поля (тег id); устанавливается по умолчанию согласно имени переменной поля
#     # 8-й параметр - словарь render_kw, передающий параметры виждету
#     name = StringField('Ваше имя?',
#                     validators=[InputRequired()])
#     email = StringField('Ваш email?',
#                      validators=[AnyInputRequired('phone', message='Одно из полей требуется (е-мэйл или телефон)'),
#                                  Email("Введите корректный е-мэйл (вида 'name@mail.com')")],
#                      render_kw={'placeholder': 'пример: your_email@mail.com'})
#     phone = StringField('Телефонный номер для связи',
#                      validators=[AnyInputRequired('email', message='Одно из полей требуется (е-мэйл или телефон)'),
#                                  Phone(message='Некорректный телефонный номер (требуется +7 (123) 456-7890)')],
#                      render_kw={'placeholder': 'пример: +7 (123) 456-7890'})
#     title = StringField('Заголовок письма')
#     text = TextAreaField('Текст письма',
#                       validators=[InputRequired(message='Текст письма требуется')])
#     submit = SubmitField('Submit',
#                       render_kw={'value': 'Отправить'})

class ProductForm(FlaskForm):

    category_id = SelectField('Категория',
                                # validators=[InputRequired()],
                                # coerce='int',
                                render_kw={'class': 'form-control'})
    prefix = StringField('Краткое описание', render_kw={'class': 'form-control'})
    manufacturer = StringField('Производитель', render_kw={'class': 'form-control'})
    model = StringField('Модель техники',
                         validators=[InputRequired()],
                         render_kw={'class': 'form-control'})
    VIN = StringField('VIN номер', render_kw={'class': 'form-control'})
    description = StringField('Подробное описание', render_kw={'class': 'form-control'})
    year = IntegerField('Год выпуска', render_kw={'class': 'form-control'})
    id = HiddenField('', default=0)
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Сохранить',
                              'class': 'btn btn-primary'
                          })

class RegionForm(FlaskForm):

    region = StringField('Название региона', render_kw={'class': 'form-control'}, validators=[InputRequired()])
    id = HiddenField('', default=0)
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Сохранить',
                              'class': 'btn btn-primary'
                          })


class IncorpForm(FlaskForm):

    kind = StringField('Организационно-правовая форма', render_kw={'class': 'form-control'}, validators=[InputRequired()])
    id = HiddenField('', default=0)
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Сохранить',
                              'class': 'btn btn-primary'
                          })


class ClientForm(FlaskForm):

    region_id = SelectField('Регион клиента',
                                # validators=[InputRequired()],
                                # coerce='int',
                                render_kw={'class': 'form-control'})
    title = StringField('Название клиента', render_kw={'class': 'form-control'})
    INN = IntegerField('ИНН клиента', render_kw={'class': 'form-control'})
    incorp_id = SelectField('Организационно-правовая форма',
                                # coerce='int',
                                render_kw={'class': 'form-control'})
    id = HiddenField('', default=0)
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Сохранить',
                              'class': 'btn btn-primary'
                          })


class ContractForm(FlaskForm):

    number = StringField('Номер контракта',
                                validators=[InputRequired()],
                                render_kw={'class': 'form-control'})
    begin_date = DateField('Дата начала договора', render_kw={'class': 'form-control', 'id': 'datepicker_begin'})
    end_date = DateField('Дата окончания договора', render_kw={'class': 'form-control', 'id': 'datepicker_end'})
    client_id = SelectField('Лизингополучатель', render_kw={'class': 'form-control'})
    comission = FloatField('Комиссия', render_kw={'class': 'form-control'})
    transfer_date = DateField('Дата передачи техники', render_kw={'class': 'form-control', 'id': 'datepicker_transfer'})
    product_id = SelectField('Название техники', render_kw={'class': 'form-control'})
    quantity = IntegerField('Количество', render_kw={'class': 'form-control'})
    manager = StringField('Менеджер', render_kw={'class': 'form-control'})
    total = IntegerField('Сумма договора', render_kw={'class': 'form-control'})
    lastpay_date = DateField('Дата последнего платежа', render_kw={'class': 'form-control', 'id': 'datepicker_lastpay'})
    id = HiddenField('', default=0)
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Сохранить',
                              'class': 'btn btn-primary'
                          })


class ChoiceContractForm(FlaskForm):

    contract = SelectField('Выбор контракта', render_kw={'class': 'form-control'})
    action = HiddenField('', default='choice')
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Выбрать',
                              'class': 'btn btn-primary'
                          })


class PortfolioDateForm(FlaskForm):

    portfolio_date = DateField('Выбор даты просмотра лизингового портфеля', render_kw={'class': 'form-control', 'id': 'datepicker_begin'})
    table_view = RadioField('', choices=['все', 'должники'], default='все',
                            render_kw={'class': 'form-check form-check-input list-unstyled d-flex list-group-horizontal justify-content-between w-100'})
    action = HiddenField('', default='portfolio_date')
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Выбрать дату',
                              'class': 'btn btn-primary'
                          })


class TransferForm(FlaskForm):

    transfer_date = DateField('Выбор года действия лизингового портфеля', render_kw={'class': 'form-control', 'id': 'datepicker_begin'})
    table_view = RadioField('', choices=['менеджеры', 'месяцы', 'кварталы'], default='менеджеры',
                            render_kw={'class': 'form-check form-check-input list-unstyled d-flex list-group-horizontal justify-content-around w-100'})
    # action = HiddenField('', default='portfolio_date')
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Выбрать год и тип вывода',
                              'class': 'btn btn-primary'
                          })


class StorageForm(FlaskForm):

    product_id = SelectField('Наименование техники', render_kw={'class': 'form-control'})
    qty = IntegerField('Количество', render_kw={'class': 'form-control'})
    total = IntegerField('Стоимость', render_kw={'class': 'form-control'})
    receipt_date = DateField('Дата поступления', render_kw={'class': 'form-control', 'id': 'datepicker_receipt'})
    expense_date = DateField('Дата расхода', render_kw={'class': 'form-control', 'id': 'datepicker_expense'})
    id = HiddenField('', default=0)
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Сохранить',
                              'class': 'btn btn-primary'
                          })


class StorageGroupForm(FlaskForm):

    # transfer_date = DateField('Выбор года действия лизингового портфеля', render_kw={'class': 'form-control', 'id': 'datepicker_begin'})
    table_view = RadioField('', choices=['без группировки', 'по категориям', 'по производителю'], default='без группировки',
                            render_kw={'class': 'form-check form-check-input list-unstyled d-flex list-group-horizontal justify-content-around w-100'})
    # action = HiddenField('', default='portfolio_date')
    submit = SubmitField('Submit',
                          render_kw={
                              'value': 'Выбрать тип группировки',
                              'class': 'btn btn-primary'
                          })