from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField
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