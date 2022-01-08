import logging
from aiohttp import web
import requests
import json
import argparse
import http.client
import time
from threading import Thread
from abstract import TestAbstractClass

class Finance:
    wallet = {}
    exchange_rates = {
        'rub-usd': 0,
        'rub-eur': 0,
        'usd-eur': 0
    }

class Wfo(TestAbstractClass):

    def sum_wallet():
        """Считает сумму всех средств в каждой из валют. Возвращает список сумм по порядку."""
        rub = round(Finance.wallet['rub'] + (Finance.wallet['usd'] * Finance.exchange_rates['rub-usd']) + (
                Finance.wallet['eur'] * Finance.exchange_rates['rub-eur']), 2)
        usd = round(Finance.wallet['usd'] + (Finance.wallet['eur'] * Finance.exchange_rates['usd-eur']) + (
                Finance.wallet['usd'] / Finance.exchange_rates['rub-usd']), 2)
        eur = round(Finance.wallet['eur'] + (Finance.wallet['usd'] / Finance.exchange_rates['usd-eur']) + (
                Finance.wallet['rub'] / Finance.exchange_rates['rub-eur']), 2)
        return f'sum: {rub} rub / {usd} usd / {eur} eur'


    def financial_data():
        """Последовательно выводит: список валют в кошельке и их значение, курс валют, сумму всех средств в каждой валюте"""
        wallet_data = ''
        for key, value in Finance.wallet.items():
            wallet_data += f" {key}: {value}\n"
        wallet_data += f"\n"
        for key, value in Finance.exchange_rates.items():
            wallet_data += f" {key}: {value}\n"
        wallet_data += f"\n"
        wallet_data += Wfo.sum_wallet()
        return wallet_data



    def update_exchange_rates(period_rates):
        """Выполняет 1 пункт тз. На вход получает период обновления в секундах.
        Парсит курс валют на текущий момент и добовляет данные в словарь."""
        while True:
            data_rate = {
                'USD': 0,
                'EUR': 0
            }
            url_rate = 'https://www.cbr-xml-daily.ru/daily_json.js'
            with requests.get(url_rate) as rate:
                dict_rate = json.loads(rate.text)
            for i in dict_rate['Valute']:
                if i in data_rate:
                    data_rate[i] = dict_rate['Valute'][i]['Value']
            Finance.exchange_rates['rub-usd'] = data_rate['USD']
            Finance.exchange_rates['rub-eur'] = data_rate['EUR']
            Finance.exchange_rates['usd-eur'] = round(data_rate['EUR'] / data_rate['USD'], 2)
            logging.info('Данные курса валют успешно обновлены.')
            time.sleep(period_rates)


    def change_control_finance(period_wallet):
        """Функция для реализации условий 5 пункта тз.
          На вход получает период обновления. Сравнивает текущие значения в кошелька и курса валют с данными из
          локальных словарей. если значения отличаются, то обновляет локальные словари и Последовательно выводит в консоль:
          список валют в кошельке и их значение, курс валют, сумму всех средств в каждой валюте.
          Изначально, локальные словари пустые, поэтому через минуту после запуска выводит данные, после раз в
          минуту, если существуют изминения."""
        test_wallet = {}
        test_exchange_rates = {}
        while True:
            time.sleep(period_wallet)
            if Finance.wallet != test_wallet or Finance.exchange_rates != test_exchange_rates:
                for key, value in Finance.wallet.items():
                    test_wallet[key] = value
                for key, value in Finance.exchange_rates.items():
                    test_exchange_rates[key] = value
                logging.info(f'\n{Wfo.financial_data()}')



    """Все что ниже, удовлетворяет требования 4 пункта тз. Запуск локального сервера, обработка post и get запросов"""

    async def get_amount(request):
        """Обробатывает гет запрос и вы водит на веб страницу: список валют в кошельке и их значение,
         курс валют, сумму всех средств в каждой валюте """
        logging.debug(request)
        response = web.Response(text=Wfo.financial_data())
        logging.debug(response)
        return response


    async def get_rub(request):
        """Обробатывает гет запрос и выводит на веб страницу: данные о количестве рублей."""
        logging.debug(request)
        rub_data = f"Рубли: {Finance.wallet['rub']}"
        response = web.Response(text=rub_data)
        logging.debug(response)
        return response


    async def get_usd(request):
        """Обробатывает гет запрос и выводит на веб страницу: данные о количестве долларов."""
        logging.debug(request)
        usd_data = f"Доллары: {Finance.wallet['usd']}"
        response = web.Response(text=usd_data)
        logging.debug(response)
        return response


    async def get_eur(request):
        """Обробатывает гет запрос и выводит на веб страницу: данные о количестве евро."""
        logging.debug(request)
        eur_data = f"Евро: {Finance.wallet['eur']}"
        response = web.Response(text=eur_data)
        logging.debug(response)
        return response


    async def post_wallet(request):
        """Обробатывает post запрос с входящим json и меняет количество валюты в кошельке на данные из json"""
        logging.debug(request)
        data = await request.text()
        data_dict = json.loads(data)
        for key, value in data_dict.items():
            if value < 0:
                logging.debug(web.Response(text='В кошельке не может быть отрицательных значений.'))
                return web.Response(text='В кошельке не может быть отрицательных значений.')
            else:
                Finance.wallet[key] = value


    async def post_change_wallet(request):
        """Обробатывает post запрос с входящим json и суммирует
        указанное в json количество валюты к существующему в кошельке"""
        logging.debug(request)
        data = await request.text()
        data_dict = json.loads(data)
        for key, value in data_dict.items():
            if (Finance.wallet[key] + value) < 0:
                Finance.wallet[key] = 0
            else:
                Finance.wallet[key] += value

"""Получает аргументы для 1,2,3 пунктов тз."""
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--period", type=int, nargs='?', const='1', default='1',
                    help="period for receiving data on exchange rates. in minutes")
parser.add_argument("-r", "--rub", type=float, nargs='?', const='0', default='0',
                    help="")
parser.add_argument("-u", "--usd", type=float, nargs='?', const='0', default='0',
                    help="")
parser.add_argument("-e", "--eur", type=float, nargs='?', const='0', default='0',
                    help="")
parser.add_argument("-d", "--debug", nargs='?', const='1', default='1',
                    help="allowable values: 0, 1, true, false, True, False, y, n, Y, N")
args = parser.parse_args()

Finance.wallet['rub'] = args.rub
Finance.wallet['eur'] = args.eur
Finance.wallet['usd'] = args.usd

"""Выполняет третий пункт тз. Обрабатывает либо положительное, либо отрицательное значение аргумента debag"""
if args.debug in ('1', 'false', 'False', 'n', 'N'):
    logging.basicConfig(
        format='%(threadName)s %(levelname)s: %(message)s',
        level=logging.INFO)
elif args.debug in ('0', 'true', 'True', 'y', 'Y'):
    logging.basicConfig(
        format='%(threadName)s %(levelname)s: %(message)s',
        level=logging.DEBUG)
else:
    print('Не верное значение параметра --debug')

logging.info('Старт потоков.')
flow_update_exchange_rates = Thread(target=Wfo.update_exchange_rates, args=(args.period * 60,), daemon=True)
flow_change_control_finance = Thread(target=Wfo.change_control_finance, args=(60,), daemon=True)
flow_update_exchange_rates.start()
flow_change_control_finance.start()

app = web.Application()
app.add_routes([
    web.get('/amount/get', Wfo.get_amount),
    web.get('/rub/get', Wfo.get_rub),
    web.get('/usd/get', Wfo.get_usd),
    web.get('/eur/get', Wfo.get_eur),
    web.post('/amount/set', Wfo.post_wallet),
    web.post('/modify', Wfo.post_change_wallet)
])

logging.info('Старт локального сервера.')
web.run_app(app, host='0.0.0.0', port=8080)
