#!/usr/bin/python3
import logging
import hashlib

import requests


class Client:


    def __init__(self, slid_token = None, app_id = None, app_secret = None,
                 user_login = None, user_password = None):
        # действует один год надо сохранять ограничение на число запросов
        self.slid_token = slid_token
        self.app_id = app_id
        self.app_secret = app_secret
        self.user_login = user_login
        self.user_password = user_password


    def auth(self):
        if not self.slid_token:
            self.app_code = self.get_app_code(self.app_id, self.app_secret)
            self.app_token = self.get_app_token(self.app_id, self.app_secret, self.app_code)
            self.slid_token = self.get_slid_user_token(self.app_token, self.user_login, self.user_password)

        # 24 часа
        user_info = self.get_slnet_token(self.slid_token)
        self.user_id = user_info["user_id"]
        self.slnet_token = user_info["slnet_token"]


    def get_app_code(self, app_id, app_secret):
        """
        Получение кода приложения для дальнейшего получения токена.
        Идентификатор приложения и пароль выдаются контактным лицом СтарЛайн.
        Срок годности кода приложения 1 час.
        :param app_id: Идентификатор приложения
        :param app_secret: Пароль приложения
        :return: Код, необходимый для получения токена приложения
        """
        url = 'https://id.starline.ru/apiV3/application/getCode/'
        logging.info('execute request: {}'.format(url))

        payload = {
            'appId': app_id,
            'secret': hashlib.md5(app_secret.encode('utf-8')).hexdigest()
        }
        r = requests.get(url, params=payload)
        response = r.json()
        logging.info('payload : {}'.format(payload))
        logging.info('response info: {}'.format(r))
        logging.info('response data: {}'.format(response))
        if int(response['state']) == 1:
            app_code = response['desc']['code']
            logging.info('Application code: {}'.format(app_code))
            return app_code
        raise Exception(response)

    def get_app_token(self, app_id, app_secret, app_code):
        """
        Получение токена приложения для дальнейшей авторизации.
        Время жизни токена приложения - 4 часа.
        Идентификатор приложения и пароль можно получить на my.starline.ru.
        :param app_id: Идентификатор приложения
        :param app_secret: Пароль приложения
        :param app_code: Код приложения
        :return: Токен приложения
        """
        url = 'https://id.starline.ru/apiV3/application/getToken/'
        logging.info('execute request: {}'.format(url))
        payload = {
            'appId': app_id,
            'secret': hashlib.md5((app_secret + app_code).encode('utf-8')).hexdigest()
        }
        r = requests.get(url, params=payload)
        response = r.json()
        logging.info('payload: {}'.format(payload))
        logging.info('response info: {}'.format(r))
        logging.info('response data: {}'.format(response))
        if int(response['state']) == 1:
            app_token = response['desc']['token']
            logging.info('Application token: {}'.format(app_token))
            return app_token
        raise Exception(response)

    def get_slid_user_token(self, app_token, user_login, user_password):
        """
         Аутентификация пользователя по логину и паролю.
         Неверные данные авторизации или слишком частое выполнение запроса авторизации с одного
         ip-адреса может привести к запросу капчи.
         Для того, чтобы сервер SLID корректно обрабатывал клиентский IP,
         необходимо проксировать его в параметре user_ip.
         В противном случае все запросы авторизации будут фиксироваться для IP-адреса сервера приложения, что приведет к частому требованию капчи.
        :param sid_url: URL StarLineID сервера
        :param app_token: Токен приложения
        :param user_login: Логин пользователя
        :param user_password: Пароль пользователя
        :return: Токен, необходимый для работы с данными пользователя. Данный токен потребуется для авторизации на StarLine API сервере.
        """
        url = 'https://id.starline.ru/apiV3/user/login/'
        logging.info('execute request: {}'.format(url))
        payload = {
            'token': app_token
        }
        data = {}
        data["login"] = user_login
        data["pass"] = hashlib.sha1(user_password.encode('utf-8')).hexdigest()
        r = requests.post(url, params=payload, data=data)
        response = r.json()
        logging.info('payload : {}'.format(payload))
        logging.info('response info: {}'.format(r))
        logging.info('response data: {}'.format(response))
        if int(response['state']) == 1:
            slid_token = response['desc']['user_token']
            logging.info('SLID token: {}'.format(slid_token))
            return slid_token
        raise Exception(response)

    def get_slnet_token(self, slid_token):
        """
        Авторизация пользователя по токену StarLineID. Токен авторизации предварительно необходимо получить на сервере StarLineID.
        :param slid_token: Токен StarLineID
        :return: Токен пользователя на StarLineAPI
        """
        url = 'https://developer.starline.ru/json/v2/auth.slid'
        logging.info('execute request: {}'.format(url))
        data = {
            'slid_token': slid_token
        }
        r = requests.post(url, json=data)
        response = r.json()
        logging.info('response info: {}'.format(r))
        logging.info('response data: {}'.format(response))
        slnet_token = r.cookies["slnet"]
        user_id = response["user_id"]
        logging.info('slnet token: {}'.format(slnet_token))
        logging.info('user_id: {}'.format(user_id))
        return { 'slnet_token': slnet_token, 'user_id': user_id }


    def get_user_info(self):
        """
        Получение списка устройств принадлежиших пользователю или устройств, доступ к которым предоставлен пользователю
         другими пользователями. Ответ содержит полное состояние устройств.
        :param user_id: user identifier
        :param slnet_token: StarLineAPI Token
        :return: Код, необходимый для получения токена приложения
        """
        self.auth()
        url = "https://developer.starline.ru/json/v2/user/{}/user_info".format(self.user_id)
        logging.info('execute request: {}'.format(url))

        r = requests.get(url, headers={"Cookie": "slnet=" + self.slnet_token})
        response = r.json()
        logging.info('response info: {}'.format(response))
        return response

    def get_obd_params(self, device_id):
        """
        Запрос данных, полученных от автомобиля и хранящихся в кеше.
        Любой из возвращаемых параметров (fuel, errors, mileage) может быть null - это значит,
        что либо он еще не считан с автомобиля системой, либо данное ТС не поддерживается установленной версией CAN
        библиотеки, либо данные невозможно считать через CAN.
        """
        url = "https://developer.starline.ru/json/v1/device/{}/obd_params".format(device_id)
        logging.info('execute request: {}'.format(url))

        r = requests.get(url, headers={"Cookie": "slnet=" + self.slnet_token})
        response = r.json()
        logging.info('response info: {}'.format(response))
        return response






