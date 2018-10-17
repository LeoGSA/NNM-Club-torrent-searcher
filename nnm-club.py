# coding: utf-8
# © LeoGSA - Sergey Grigoriev (leogsa@gmail.com)

import requests
import lxml.html as html
import os
import re

cookies = False

class NNMClub(object):

    url = 'http://nnmclub.to/forum/'

    def auth(self, username, password):
        """
        ENG: This module goes through authorization and saves cookies to a global variable.
        RUS: Этот модуль авторизуется на сайте и сохраняет кукисы в глобальную переменную.
        """

        session = requests.Session()
        url = self.url + 'login.php'
        payload = {
            'username' : username,
            'password' : password,
            'autologin' : 'on',
            'redirect' : '',
            'code' : '536958ef20737935', # take from browser
            'login' : 'Вход'
        }

        headers = {

        'Host' : 'nnmclub.to',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding' : 'gzip, deflate',
        'Referer' : 'http://nnmclub.to/forum/login.php',
        'Connection' : 'keep-alive'
        }

        r = session.post(url, data=payload, headers=headers)
        global cookies
        cookies = session.cookies

    def search_list_txt_parser(self):
        """
        ENG: Opens the search_list.txt file from the program directory and parses it. Returns films list.
        RUS: Открывает и парсит файл search_list.txt из той же папки, где программа,
        возвращает список с названиями фильмов.
        """

        search_list = []

        with open('search_list.txt', 'r') as file:
            for line in file:
                if line.startswith('#') or line == '\n':
                    continue
                search_list.append(line.strip().lower())

        return search_list

    def search(self, string_to_search):
        """
        ENG: This module makes a search on a tracker by string_to_search. Returns a page with search results.
        RUS: Этот модуль выполняет поиск на трекере по строке string_to_search,
        возвращает страницу с результатами поиска.
        """

        url = self.url + "tracker.php"

        headers = {

        'Host' : 'nnmclub.to',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language' : 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding' : 'gzip, deflate',
        'Referer' : 'http://nnmclub.to/forum/login.php',
        'Connection' : 'keep-alive'
        }

        string_to_search_converted = string_to_search.replace(' ', '+').encode('cp1251')

        payload = {
            'prev_sd' : 0,
            'prev_a' : 0,
            'prev_my' : 0,
            'prev_n' : 0,
            'prev_shc' : 0, # показывать колонку Категория
            'prev_shf' : 1, # показывать колонку Форум
            'prev_sha' : 1, # показывать колонку Автор
            'prev_shs' : 0, # показывать колонку Скорость
            'prev_shr' : 0, # показывать колонку Рейтинг
            'prev_sht' : 0, # показывать колонку Спасибо
            'f[]' : -1, # категории, где искать. '-1' = 'все имеющиеся'
            'o' : 1, # 1 - зарегистрирован, 4 - скачан, 7 - размер
            's' : 2, # 1 - по возрастанию, 2 - по убыванию
            'tm' : 7, # 30 - посл месяц, 7 - за посл неделю, -1 - за все время
            'shf' : 1,
            'sha' : 1,
            'ta' : -1,
            'sns' : -1,
            'sds' : -1,
            'nm' : string_to_search_converted,
            'pn' : '',
            'submit' : 'Поиск'
        }

        page = requests.post(url, data=payload, cookies=cookies, headers=headers)

        return page

    def analize_search_result(self, page):
        """
        ENG: Takes a page with search results, parses it and returns a list of lines with results.
        RUS: Получает страницу с результатами поиска, парсит её и возвращает список строк
        """

        page = page.content

        res = html.fromstring(page)

        list_of_lines = res.xpath(u".//*[@id='search_form']/table[3]/tbody/tr")

        movie_good_forum_list = [
        'Новинки (HD)', 'Архив Видео', 'Фильмы в оригинале (HD)',
        'Зарубежные Новинки (HD*Rip/LQ, DVDRip)', 'Фильмы в оригинале'
        ]

        movie_bad_forum_list = ['Экранки', 'Архив неактуальных экранок', 'OST', 'OST (Lossless)', 'Трейлеры']

        lenth = len(list_of_lines)
        if lenth > 8:
            lenth = 8

        string_list = []

        if lenth == 0:
            print ('Ничего не найдено')
            string_list.append('Ничего не найдено')

        for i in range(0, lenth):
            forum_type = res.xpath(u".//*[@id='search_form']/table[3]/tbody/tr[%s]/td[2]/a/text()" % str(i+1))[0]

            if forum_type not in movie_bad_forum_list:
                line_name = res.xpath(u".//*[@id='search_form']/table[3]/tbody/tr[%s]/td[3]/a/b/text()" % str(i+1))[0]
                size = res.xpath(u".//*[@id='search_form']/table[3]/tbody/tr[%s]/td[6]/text()" % str(i+1))[0]
                pre_link = res.xpath(u".//*[@id='search_form']/table[3]/tbody/tr[%s]/td[3]/a/@href" % str(i+1))[0]
                link = self.url + re.search(r'(viewtopic\.php\?t=\d+)', pre_link).group(1)
                print(forum_type+' -- '+line_name+' -- '+size+'\n'+link+'\n')
                string_list.append(forum_type+' -- '+line_name+' -- '+size+'\n'+link)

        return string_list

    def general(self, username, password):
        """
        ENG: Runs other modules in needed order. Writes results to a file result_list.txt.
        RUS: Запускает другие модули в нужном порядке. Записывает результаты в файл result_list.txt.
        """

        self.auth(username, password)
        film_list = self.search_list_txt_parser()

        output_lines = []

        for i in film_list:
            output_lines.append((i, self.analize_search_result(self.search(i))))

        with open('result_list.txt', 'w') as file:
            for name, string_list in output_lines:
                file.write(name+'\n')
                for line in string_list:
                    file.write(line+'\n')
                file.write('\n')
        os.startfile('result_list.txt')


if __name__ == '__main__':
    nnmclub = NNMClub()

    # Enter your NNM-Club username and password here
    username = ''
    password = ''

    nnmclub.general(username, password)

    # testing branches.
