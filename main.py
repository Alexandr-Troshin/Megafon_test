import pandas as pd
import numpy as np
import datetime
import telegram


def generate_customer(qty_cust, cur_dttm):
    """ Функция генерирует нового пользователя с рандомным балансом, возрастом, городом и тарифом.
        Данные по тарифу берутся из датафрейма тарифов.
        :param qty_cust - количество пользователей в базе
        :param cur_dttm - текущее время создания пользователя
        :return список с характеристиками пользователя (id, баланс, дата создания, возраст,
                город, время создания, тариф, количество минут, смс и мегабайт)"""
    global city_lst
    global rates_df
    global rng
    balance = rng.integers(0, 300)
    age = rng.integers(18, 60)
    city = np.random.choice(city_lst)
    rate = np.random.choice(rates_df.name)
    return [qty_cust+1, balance, cur_dttm.strftime('%d-%m-%y'), age, city,
            cur_dttm.strftime('%d-%m-%y %H:%m'), rate,
            rates_df[rates_df.name == rate].minutes_incl.values[0],
            rates_df[rates_df.name == rate].sms_incl.values[0],
            rates_df[rates_df.name == rate].mb_incl.values[0]]


def generate_event(qty_cust):
    """ Функция генерирует событие (звонок, смс или трафик) для произвольного абонента
        из qty_cust абонентов со случайным количетсвом израсходованных единиц (кроме смс- только 1)
        :param - количество абонентов в базе
        :return - список из id абонента, типа события и количества израсходованных единиц.
        """
    global rng
    events_type_lst = ['звонок', 'смс', 'трафик']
    cust_id = rng.integers(1, qty_cust)
    event_type = np.random.choice(events_type_lst)
    if event_type == 'звонок':
        event_cost = rng.integers(1, 15)
    elif event_type == 'смс':
        event_cost = 1
    else:
        event_cost = rng.integers(1, 3000)
    return [cust_id, event_type, event_cost]


def send_alert(cust_id, srv_kind, is_send_tg):
    """ Функция создания оповещения о достижении лимита на экран и в телеграмм-чат.
        Для отправки в телеграмм-чат неоходимо указать token и chat_id.
    :param cust_id - id пользователя
    :param srv_kind - тип ресурса по которому закончился лимит
    :param is_send_tg - отпрвлять ли отчет в телеграмм-чат"""
    if is_send_tg:
        bot = telegram.Bot(token='_____________________')
        chat_id = 0000000000
        msg = '''У пользователя {cust_id} закончился лимит {srv_kind}'''
        report = msg.format(cust_id=str(cust_id), srv_kind=srv_kind)
        bot.sendMessage(chat_id=chat_id, text=report)

    print('У пользователя ' + str(cust_id) + 'закончился лимит ' + srv_kind)


if __name__ == '__main__':
    # создаем список городов
    city_lst = ['Москва' for _ in range(10)] + ['Санкт-Петербург' for _ in range(7)] + \
               ['Саратов' for _ in range(2)]
    # создаем датафрейм с тарифами
    rng = np.random.default_rng()
    rates_data = {'id': [1, 2, 3],
                  'name': ['МегаТариф', 'Максимум', 'VIP'],
                  'date_from': ['15.03.2022', '15.03.2022', '15.03.2022'],
                  'date_to': ['31.12.2022', '31.12.2022', '31.12.2022'],
                  'minutes_incl': [800, 1200, 1700],
                  'sms_incl': [300, 300, 300],
                  'mb_incl': [35000, 50000, 50000]}
    rates_df = pd.DataFrame(rates_data)
    # создаем пустые датафреймы событий и пользователей
    events_df = pd.DataFrame(columns=['id', 'event_dttm', 'cust_id', 'event_type', 'event_cost'])
    cust_df = pd.DataFrame(columns=['id', 'balance', 'add_date', 'age', 'city', 'last_actitvity_dttm',
                                    'rate', 'minutes', 'sms', 'mb'])
    # первым днем принимаем 01 января 2022 года
    start_day = datetime.datetime(2022, 1, 1)
    # добавим стартовых пользователей
    for i in range(5):
        cust_df.loc[i] = generate_customer(len(cust_df), start_day)
    # запускаем цикл по дням... в пределах дня происходят события
    for day in range(10):
        daily_events_df = pd.DataFrame(columns=['id', 'event_dttm', 'cust_id', 'event_type', 'event_cost'])
        cur_date = start_day + datetime.timedelta(days=day)
        # к началу дня добавляем произволльное число минут - для определения времени события
        add_time = rng.integers(1, 60)
        # события генерируются до завершения суток
        while add_time < 24*60:
            # генерируем тип события 2% событий - создание нового пользователя
            # остальные - совершение расходной операции
            generation_choice = rng.integers(0, 100)
            if generation_choice < 2:
                cust_df.loc[len(cust_df)] = generate_customer(len(cust_df), start_day)
            else:
                # генерируем событие использования тарифа
                event = generate_event(len(cust_df))
                # в дальнейшем при отрицательном остатке соответвующих единиц
                # событие считается невозможным
                # если в процессе события остаток стал < 0 - отправляется уведомление
                is_possible_event = True
                if event[1] == 'звонок':
                    if cust_df[cust_df.id == event[0]].minutes.values[0] > 0:
                        cust_df.loc[cust_df.id == event[0], 'minutes'] = \
                            cust_df[cust_df.id == event[0]].minutes.values[0] - event[2]
                        if cust_df[cust_df.id == event[0]].minutes.values[0] <= 0:
                            send_alert(event[0], 'доступных минут', False)
                    else:
                        is_possible_event = False
                elif event[1] == 'смс':
                    if cust_df[cust_df.id == event[0]].sms.values[0] > 0:
                        cust_df.loc[cust_df.id == event[0], 'sms'] = \
                            cust_df[cust_df.id == event[0]].sms.values[0] - event[2]
                        if cust_df[cust_df.id == event[0]].sms.values[0] <= 0:
                            send_alert(event[0], 'доступных СМС', False)
                    else:
                        is_possible_event = False
                else:
                    if cust_df[cust_df.id == event[0]].mb.values[0] > 0:
                        cust_df.loc[cust_df.id == event[0], 'mb'] = \
                            cust_df[cust_df.id == event[0]].mb.values[0] - event[2]
                        if cust_df[cust_df.id == event[0]].mb.values[0] <= 0:
                            send_alert(event[0], 'доступного трафика', False)
                    else:
                        is_possible_event = False
                if is_possible_event:
                    daily_events_df.loc[len(daily_events_df)] = \
                        [len(daily_events_df), cur_date + datetime.timedelta(minutes=int(add_time))] + \
                        event
            add_time += rng.integers(1, 60)

        daily_report = pd.pivot_table(daily_events_df,
                                      index='cust_id',
                                      columns='event_type',
                                      values='event_cost',
                                      aggfunc='sum')
        print('Отчет за ', cur_date.date())
        print(daily_report)
        events_df = pd.concat([events_df, daily_events_df], ignore_index=True)
        input('Для перехода в следующий день нажмите Enter')
