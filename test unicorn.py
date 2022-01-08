# import aiohttp
import logging
from aiohttp import web
import requests
import json
import argparse
import http.client
# import asyncio
# import concurrent.futures
# from concurrent.futures import ThreadPoolExecutor
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
        for i, l in Finance.wallet.items():
            wallet_data += f" {i}: {l}\n"
        wallet_data += f"\n"
        for i, l in Finance.exchange_rates.items():
            wallet_data += f" {i}: {l}\n"
        wallet_data += f"\n"
        wallet_data += Wfo.sum_wallet()
        return wallet_data

# """Получает аргументы для 1,2,3 пунктов тз."""
# parser = argparse.ArgumentParser()
# parser.add_argument("-p", "--period", type=int, nargs='?', const='1', default='1',
#                     help="period for receiving data on exchange rates. in minutes")
# parser.add_argument("-r", "--rub", type=float, nargs='?', const='0', default='0',
#                     help="")
# parser.add_argument("-u", "--usd", type=float, nargs='?', const='0', default='0',
#                     help="")
# parser.add_argument("-e", "--eur", type=float, nargs='?', const='0', default='0',
#                     help="")
# parser.add_argument("-d", "--debug", nargs='?', const='1', default='1',
#                     help="allowable values: 0, 1, true, false, True, False, y, n, Y, N")
# args = parser.parse_args()
#
# Finance.wallet['rub'] = args.rub
# Finance.wallet['eur'] = args.eur
# Finance.wallet['usd'] = args.usd
#
# """Выполняет третий пункт тз. Обрабатывает либо положительное, либо отрицательное значение аргумента debag"""
# if args.debug in ('1', 'false', 'False', 'n', 'N'):
#     logging.basicConfig(
#         format='%(threadName)s %(levelname)s: %(message)s',
#         level=logging.WARNING)
# elif args.debug in ('0', 'true', 'True', 'y', 'Y'):
#     # http.client.HTTPConnection.debuglevel = 1
#     #
#     # logging.basicConfig(format='%(threadName)s %(levelname)s: %(message)s')
#     # logging.getLogger().setLevel(logging.DEBUG)
#     # requests_log = logging.getLogger("requests.packages.urllib3")
#     # requests_log.setLevel(logging.DEBUG)
#     # requests_log.propagate = True
#     logging.basicConfig(
#         format='%(threadName)s %(levelname)s: %(message)s',
#         level=logging.DEBUG)
# else:
#     print('Не верное значение параметра --debug')


    def update_exchange_rates(n):
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
            logging.warning('Данные курса валют успешно обновлены.')
            time.sleep(n)


    def change_control_finance(f):
        """Функция для реализации условий 5 пункта тз.
          На вход получает период обновления. Сравнивает текущие значения в кошелька и курса валют с данными из
          локальных словарей. если значения отличаются, то обновляет локальные словари и Последовательно выводит в консоль:
          список валют в кошельке и их значение, курс валют, сумму всех средств в каждой валюте.
          Изначально, локальные словари пустые, поэтому через минуту после запуска выводит данные, после раз в
          минуту, если существуют изминения."""
        test_wallet = {}
        test_exchange_rates = {}
        while True:
            time.sleep(f)
            if Finance.wallet != test_wallet or Finance.exchange_rates != test_exchange_rates:
                for i, l in Finance.wallet.items():
                    test_wallet[i] = l
                for i, l in Finance.exchange_rates.items():
                    test_exchange_rates[i] = l
                logging.warning(f'\n{Wfo.financial_data()}')


# logging.warning('Старт потоков.')
# flow_update_exchange_rates = Thread(target=update_exchange_rates, args=(args.period * 60,), daemon=True)
# flow_change_control_finance = Thread(target=change_control_finance, args=(60,), daemon=True)
# flow_update_exchange_rates.start()
# flow_change_control_finance.start()

    """Все что ниже, удовлетворяет требования 4 пункта тз. Запуск локального сервера, обработка post и get запросов"""

    async def get_amount(request):
        """Обробатывает гет запрос и вы водит на веб страницу: список валют в кошельке и их значение,
         курс валют, сумму всех средств в каждой валюте """
        logging.debug(request)
        # response = web.Response()
        # test = financial_data()
        # web.Response.headers['Content-Type'] = 'text/html'
        # await response.prepare(request)
        # await response.write(test)

        logging.debug(web.Response(text=Wfo.financial_data()))
        return web.Response(text=Wfo.financial_data())


    async def get_rub(request):
        """Обробатывает гет запрос и выводит на веб страницу: данные о количестве рублей."""
        logging.debug(request)
        rub_data = f"Рубли: {Finance.wallet['rub']}"
        logging.debug(web.Response(text=rub_data))
        return web.Response(text=rub_data)


    async def get_usd(request):
        """Обробатывает гет запрос и выводит на веб страницу: данные о количестве долларов."""
        logging.debug(request)
        usd_data = f"Доллары: {Finance.wallet['usd']}"
        logging.debug(web.Response(text=usd_data))
        return web.Response(text=usd_data)


    async def get_eur(request):
        """Обробатывает гет запрос и выводит на веб страницу: данные о количестве евро."""
        logging.debug(request)
        eur_data = f"Евро: {Finance.wallet['eur']}"
        logging.debug(web.Response(text=eur_data))
        return web.Response(text=eur_data)


    async def post_wallet(request):
        """Обробатывает post запрос с входящим json и меняет количество валюты в кошельке на данные из json"""
        logging.debug(request)
        data = await request.text()
        data_dict = json.loads(data)
        for i, l in data_dict.items():
            if l < 0:
                logging.debug(web.Response(text='В кошельке не может быть отрицательных значений.'))
                return web.Response(text='В кошельке не может быть отрицательных значений.')
            else:
                Finance.wallet[i] = l


    async def post_change_wallet(request):
        """Обробатывает post запрос с входящим json и суммирует
        указанное в json количество валюты к существующему в кошельке"""
        logging.debug(request)
        data = await request.text()
        data_dict = json.loads(data)
        for i, l in data_dict.items():
            if (Finance.wallet[i] + l) < 0:
                Finance.wallet[i] = 0
            else:
                Finance.wallet[i] += l

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
        level=logging.WARNING)
elif args.debug in ('0', 'true', 'True', 'y', 'Y'):
    # http.client.HTTPConnection.debuglevel = 1
    #
    # logging.basicConfig(format='%(threadName)s %(levelname)s: %(message)s')
    # logging.getLogger().setLevel(logging.DEBUG)
    # requests_log = logging.getLogger("requests.packages.urllib3")
    # requests_log.setLevel(logging.DEBUG)
    # requests_log.propagate = True
    logging.basicConfig(
        format='%(threadName)s %(levelname)s: %(message)s',
        level=logging.DEBUG)
else:
    print('Не верное значение параметра --debug')

logging.warning('Старт потоков.')
flow_update_exchange_rates = Thread(target=Wfo.update_exchange_rates, args=(args.period * 60,), daemon=True)
flow_change_control_finance = Thread(target=Wfo.change_control_finance, args=(60,), daemon=True)
flow_update_exchange_rates.start()
flow_change_control_finance.start()

# headers = {'content-type': 'text/plain'}
app = web.Application()
app.add_routes([
    web.get('/amount/get', Wfo.get_amount),
    web.get('/rub/get', Wfo.get_rub),
    web.get('/usd/get', Wfo.get_usd),
    web.get('/eur/get', Wfo.get_eur),
    web.post('/amount/set', Wfo.post_wallet),
    web.post('/modify', Wfo.post_change_wallet)
])

logging.warning('Старт локального сервера.')
web.run_app(app, host='0.0.0.0', port=8080)

