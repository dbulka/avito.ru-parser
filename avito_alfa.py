import requests
from bs4 import BeautifulSoup
import csv
import time
import json


# использем requests.get для отправки запросов  на сайт
def get_html(url):
    r = requests.get(url)
    # print(r.text)
    return r.text

# используем beatifulsoup для парсинга сайта, эта функция определяет количество страниц с вакансиями на сайте
def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    page_catalog = soup.find('div', class_='pagination')
    #   print(page_catalog)
    # парсим строку с ссылками на стариницы, выбираем последнюю и выводим её как общее количество
    total_pages = page_catalog.find_all('a', class_='pagination-page')[-1].get('href').split('=')[1]
    print('total_pages =', total_pages)
    return int(total_pages)

# переходим в необходимые для нас разделы сайта и формируем базу данных заданного количества вакансий (исключая блэклист и уже сохранённые вакансии)
def get_page_data(html, bl_json, data_json, total_vacs, read_json):
    list_data = []
    read_json = []
    i = 0
    soup = BeautifulSoup(html, 'lxml')
    # парсим список вакансий начиная с первой страницы
    ads = soup.find('div', class_='js-catalog-list').find_all('div', class_='description')
    n = 0
    # цикл необходим для поочерёдного занесения данных для каждой вакансии
    for ad in ads:
        # счётчик вакансий фиксирует сколько вакансий сохранено в базе данных
        if n != total_vacs:
            # используем try/except что бы исключить ошибку если отсутствует "название вакансии"
            try:
                vac_name = ad.find('h3', class_='title').text.strip()
            except:
                vac_name = 'None vac_name'
            print(vac_name)
    # цикл меняет все символы на пробелы в названии вакансии и split() разбивает строку-название на список-слов
            for char in '-,!@#$%^&*()_+=/':
                vac_name = vac_name.replace(char, ' ')
            splited_vac_name = vac_name.split()
    # цикл проверяет нет ли слов из списка строки-"название вакансии" в блэклисте
            check = 0
            for name in splited_vac_name:
                if name.lower() in bl_json:
                    print(name, ' <=== ахтунг, блэклист хочет пролезть ')
                    check += 1
                else:
                    check += 0
            if check >= 1:
                check_name = 'BL'
            else:
                check_name = 'no BL'
            if check_name == 'BL':
                print(vac_name, ' in blacklist\n')
            else:
    # проверяем есть ли такая вакансия в базе данных results.json
                with open('results.json', 'r') as f:
                    for line in f.read().split(']'):
                        list_data.append(line)
                        data = list_data[i].strip('\'"{}[!@#$%^&*()-+]').split('":')
                        i += 1
                        data_pis = data[0].split('"')[0].lower()
                        read_json.append(data_pis)
                # print(read_json)
                if vac_name.lower() in read_json:
                    print(vac_name, ' already added\n')
    # если вакансии проходит по условия "не в blackliste", "ранеее не записана", то она записывается в базу данных results.json
                else:
                    print('- vacancy was added.')
                    n += 1
                    # парсим з/п
                    try:
                        salary = ad.find('div', class_='about').text.strip()
                    except:
                        salary = 'None salary'
                    print(salary)
                    # парсим  адрес вакансии
                    try:
                        adress = ad.find('div', class_='data').find_all('p')[-1].text.strip()
                    except:
                        adress = 'None adress'
                    print(adress)
                    # парсим  ссылку на вакансию
                    try:
                        url_hours = ad.find('a', class_='item-description-title-link').get('href')
                        main_url_hours = 'https://www.avito.ru/' + url_hours
                        hours_req = requests.get(main_url_hours)
                        hours_soup = BeautifulSoup(hours_req.text, 'lxml')
                        hours = hours_soup.find('div', class_='item-view').find('div', class_='item-view-content').find_all('li', class_='item-params-list-item')[1].text.strip()
                    except:
                        hours = 'None hours'
                    print(hours)
                    try:
                        info = main_url_hours
                    except:
                        info = "None info"
                    print(info, '\n')
                    # словарь для сохранение вакансии в базу данных results.json
                    data_json = vac_name,salary, hours, adress, info
                    # словарь для сохранение вакансии в базу данных results.csv
                    data_csv = [vac_name, salary, hours, adress, info]
                    # записываем вакансию в базу данных results.csv
                    write_csv(data_csv)
                    # записываем вакансию в базу данных results.json
                    write_json(data_json)
                    # формируем паузу, что бы обойти защиту сайта от "частых запросов"
                    time.sleep(1.5)

    print('Parsing was completed with ',n,' vacancies.')
    # передаём в page_parse сигнал об окончании парсинга
    break_val = 1
    return break_val

# записываем инфо в базу данных results.json
def write_json(data_json):
    with open("results.json", "a") as write_file:
        json.dump(data_json, write_file, ensure_ascii=False)

# сохраняем данных из results.json в список read_json
def read_json(read_json):
    with open('results.json', 'r') as f:
        for line in f.read().split(']'):
            list_data.append(line)
            data = list_data[i].strip('\'"{}[!@#$%^&*()-+]').split('":')
            i += 1
            data_pis = data[0].split('"')[0].lower()
            read_json.append(data_pis)
            print(read_json)
    return read_json

# функция управления блэклистом
def data_blacklist(bl_json):
    c = None
    while c != 'No':
        question = (str(input('Do you want add a word to blacklist? (yes/no): '))).upper()
        if question == 'YES':
            bl_word = input('Please enter word for blacklist: ').lower()
            if bl_word in bl_json:
                print(bl_word, ' already in lacklist')
            else:
                bl_json.append(bl_word)
        elif question == 'NO':
            c = 'No'
        else:
            print('please enter correct answer: \'yes\' or \'no\'')
        print('blacklist: ', bl_json, '\n')
    return bl_json

# записываем данные в блэклист
def write_blacklist(bl_json):
    with open("blacklist.json", "w") as write_blacklist:
        json.dump(bl_json, write_blacklist, ensure_ascii=False)

# считываем данные из блэклиста
def read_blacklist(bl_json):
    with open('blacklist.json', 'r') as read_blacklist:
        bl_json = json.load(read_blacklist)
    return bl_json

# функция работы блэклиста
def blacklist(bl_json):
    print('blacklist: ', read_blacklist(bl_json))
    write_blacklist(data_blacklist(read_blacklist(bl_json)))
    bl_json = read_blacklist(bl_json)
    return bl_json

# записываем данные в results.csv
def write_csv(data_csv):
    with open('results.csv', 'a') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_csv)

# парсинг страниц, если get_page_data выполнена, то парсинг заканчивается
def pars_pages(total_pages,total_vacs,bl_json, data_json,read_json):
    i = 0
    # цикл для окончания парсинга, если функция get_page_data выполнена
    while i != total_pages:
        i += 1
        print('Amount of vacancies for parsing = ', total_vacs)
        print('Page of vacancies #', i)
        main_url = 'https://www.avito.ru/moskva/vakansii/it_internet_telekom?p=' + str(i)
        break_val = get_page_data(get_html(main_url), blacklist(bl_json), data_json, total_vacs, read_json)
        if break_val == 1:
            i = total_pages
        else:
            i = 0

# дерево программы
def main():
    check_names = '---'
    bl_json = []
    data_json = {}
    read_json = []
    url = 'https://www.avito.ru/moskva/vakansii/it_internet_telekom?p=1'
    total_pages = get_total_pages(get_html(url))
    re = None
    while re != 'No':
        cont = str(input('Do you want new parsing? yes/no: ')).upper()
        if cont == 'YES':
            z = None
            while z != 'no':
                try:
                    total_vacs = int(input('How much vacancies do you want to parsing? Enter number: '))
                    z = 'no'
                except:
                    print('please enter number more carefully')
            pars_pages(total_pages,total_vacs,bl_json, data_json, read_json)
        elif cont == 'NO':
            re = 'No'
            z = 'no'
        else:
            print('please enter answer more carefully')

main()