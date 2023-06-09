from formats import bold_string
from data import settings
import requests
from loader import workbook, worksheet
from xlsxwriter import Workbook
from data import items, settings
from helpers import get_min_sell_price


headers = {'accept': '*/*', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

def init_table() -> None:
    '''Размечает таблицу'''
    worksheet.set_column('A:E', 25)
    worksheet.write('A1', 'Название предмета', bold_string)
    worksheet.write('B1', f'Мин. цена {settings.chosen_location}', bold_string)
    worksheet.write('C1', 'Мин. цена Черный Рынок', bold_string)
    worksheet.write('D1', 'Выручка', bold_string)
    worksheet.write('E1', 'Соотношение', bold_string)

def close_table(workbook: Workbook) -> None:
    '''Закрывает таблицу'''
    workbook.close()

def fill_table() -> None:
    '''Заполняет названия в первую колонку, полученные из списка предметов '''
    if settings.PREMIUM_TAX == True: 
        tax = 0.08
    else: tax = 0.13
    for j in range(len(items.item_list)):
        worksheet.write(f'A{j + 2}', items.item_list[j])
        fill_item_sell_price(j, items.item_dict_inverted[items.item_list[j]])
        fill_item_sell_price_BlackMarket(j, items.item_dict_inverted[items.item_list[j]])
        worksheet.write_formula(f'D{j + 2}', f'=(C{j + 2}-B{j + 2})*(1-{tax})')
        worksheet.write_formula(f'E{j + 2}', f'=(B{j + 2}/D{j + 2})')
    worksheet.conditional_format(f'E2:E{len(items.item_list) + 1}', {
        'type' : '3_color_scale',
        'min_color' : '#d35400',
        'mid_color' : '#f7dc6f',
        'max_color' : '#27ae60',
    })
    worksheet.conditional_format(f'D2:D{len(items.item_list) + 1}', {
        'type' : '3_color_scale',
        'min_color' : '#d35400',
        'mid_color' : '#f7dc6f',
        'max_color' : '#27ae60',
    })
    

def fill_item_sell_price(num: int , item_name: str) -> None:
    '''Получает название предмета и индекс ячейки C, вписывает цену с выбранного маркета'''
    request = requests.get(f'https://www.albion-online-data.com/api/v2/stats/prices/{item_name}.json?locations={settings.chosen_location}&qualities=0', headers=headers)
    request = request.json()
    worksheet.write(f'B{num + 2}', get_min_sell_price(request))
    if settings.DEBUG == True:
        print(request[0].get('sell_price_min_date'))

def fill_item_sell_price_BlackMarket(num: int, item_name: str) -> None:
    '''Получает название предмета и индекс ячейки B, вписывает цену с черного рынка'''
    request = requests.get(f'https://www.albion-online-data.com/api/v2/stats/prices/{item_name}.json?locations=BlackMarket&qualities=0', headers=headers).json()
    worksheet.write(f'C{num + 2}', get_min_sell_price(request))
    if settings.DEBUG == True:
        print(request[0].get('sell_price_min_date'))

