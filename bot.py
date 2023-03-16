#!venv/bin/python
import asyncio
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest

from statistic import dec_message_send_analytics
from user import User
from warehouse import WarehouseDataCollector


class BotFenix:
    def __init__(self, bot_instance, bot_dispatcher, logger: logging.Logger = None, cache=None):
        self.bot_instance = bot_instance
        self.bot_dispatcher = bot_dispatcher
        self.logger = logger
        self.cache = cache

    async def on_startup(self, dp):
        import threading
        # from notify import Notification
        from payment_worker import PaymentWorker

        await self.set_main_commands()

        # Run Notification worker
        # _notify = Notification(self)
        # asyncio.create_task(_notify.start_worker())
        # t = threading.Thread(target=asyncio.run, args=(_notify.start_worker(),))
        # t.start()

        _pay_worker = PaymentWorker(self)
        asyncio.create_task(_pay_worker.start_worker())
        # t = threading.Thread(target=asyncio.run, args=(_pay_worker.start_worker(),))
        # t.start()
        _warehouse = WarehouseDataCollector()
        _warehouse.start()

    def initialize(self):
        from commands.init import CommandsInit
        from callbacks.init import CallbackInit

        commands = [
            self.start,
            self.faq,
            self.price,
            self.news,
            self.chat,
            self.review,
            self.support,
            self.reports,
            self.buy,
        ]

        for command in commands:
            self.bot_dispatcher.register_message_handler(
                    command, commands=command.__name__.lower())

        # fallback for none commands
        self.bot_dispatcher.register_message_handler(
                self.fallback, content_types=["text"])

        # register callbacks for inline buttons
        self.bot_dispatcher.register_callback_query_handler(
                self.callback_cancel, text="cancel", state="*")

        # register other
        ob_commands = CommandsInit(self)
        ob_commands.register()

        ob_callback = CallbackInit(self)
        ob_callback.register()

    # region commands
    @dec_message_send_analytics("start")
    async def start(self, message: types.Message):
        from commands.start import Start

        ob_user = self.get_user(message)
        record = ob_user.get_user()
        ob_user.log_message(message.text)

        if 'BLOCKED' in record and record['BLOCKED']:
            ob_user.un_block()

        _start = Start(self, message)
        await _start.call()

    @dec_message_send_analytics("faq")
    async def faq(self, message: types.Message):
        from commands.faq import FAQ

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _faq = FAQ(self, message)
        await _faq.call()

    @dec_message_send_analytics("price")
    async def price(self, message: types.Message):
        from commands.price import Price

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _price = Price(self, message)
        await _price.call()

    @dec_message_send_analytics("news")
    async def news(self, message: types.Message):
        from commands.news import News

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _news = News(self, message)
        await _news.call()

    @dec_message_send_analytics("chat")
    async def chat(self, message: types.Message):
        from commands.chat import Chat

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _chat = Chat(self, message)
        await _chat.call()

    @dec_message_send_analytics("review")
    async def review(self, message: types.Message):
        from commands.review import Review

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _review = Review(self, message)
        await _review.call()

    @dec_message_send_analytics("support")
    async def support(self, message: types.Message):
        from commands.support import Support

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _support = Support(self, message)
        await _support.call()

    @dec_message_send_analytics("reports")
    async def reports(self, message: types.Message):
        from commands.reports import ReportsCommand

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _report = ReportsCommand(self, message)
        await _report.call()

    @dec_message_send_analytics("buy")
    async def buy(self, message: types.Message):
        from commands.vendor_sub_buy import VendorSubBuyCommand

        ob_user = self.get_user(message)
        ob_user.get_user()
        ob_user.log_message(message.text)

        _report = VendorSubBuyCommand(self, message)
        await _report.call(message)

    async def fallback(self, message: types.Message):
        from commands.admin_send import AdminSend
        from commands.admin_subscribe import AdminSubscribe
        from commands.admin_summary import AdminSummary
        from commands.fallback import Fallback
        from tools.server import Server

        ob_user = self.get_user(message)
        ob_user.log_message(message.text)

        await self.set_main_commands()

        if ob_user.is_admin(for_buttons=True):
            sys_actual_dates_button = self.sys_actual_dates_button()
            sys_bot_info_button = self.sys_bot_info_button()
            sys_add_subscribe_button = self.sys_add_subscribe_button()
            sys_send_message_button = self.sys_send_message_button()
            sys_server_info = self.sys_server_info()
            sys_server_restart_docker = self.sys_server_restart_docker()

            if message.text == sys_send_message_button['text']:
                _admin_send = AdminSend(self, message)
                await _admin_send.call()
                return
            elif message.text == sys_add_subscribe_button['text']:
                _admin_subscribe = AdminSubscribe(self, message)
                await _admin_subscribe.call()
                return
            elif message.text == sys_bot_info_button['text']:
                _admin_summary = AdminSummary(self, message)
                await _admin_summary.call()
                return
            elif message.text == sys_server_info['text']:
                _server = Server()
                text = _server.get_message()
                await self.answer(message, text)
                return
            elif message.text == sys_server_restart_docker['text']:
                _server = Server()
                text = _server.restart_docker()
                await self.answer(message, text)
                return

        ob_fallback = Fallback(self, message)
        await ob_fallback.answer(message)
        # await self.answer(message, "Команда ({}) не распознана!".format(message.text))

    async def callback_cancel(self, call: types.CallbackQuery, state: FSMContext):
        from commands.start import Start

        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()

        _start = Start(self, call.message)
        try:
            await _start.call(type_send="edit")
        except:
            pass

        await call.answer()

    # endregion

    # region utils
    async def answer(self, _message, text, keyboard=None):
        return await self.send(_message, text, keyboard)

    async def reply(self, _message, text, keyboard=None):
        try:
            return await self.send(_message, text, keyboard, type_send="reply")
        except BadRequest as e:
            if e.text == "Replied message not found":
                self.logger.info(f"Не найдено сообщение для ответа")
            else:
                self.logger.error(e)

    async def edit_text(self, _message, text, keyboard=None, save_reply=False):
        return await self.send(_message, text, keyboard, type_send="edit", save_reply=save_reply)

    async def send_photo(self, _message, photo_path, keyboard=None, caption=None, type_send="answer_photo"):
        return await self.send(_message, caption, keyboard, photo_path=photo_path, type_send=type_send)

    async def send(self, _message, text, keyboard=None, type_send="answer", photo_path=None, save_reply=False):
        ob_user = self.get_user(_message)

        reply_markup = {'remove_keyboard': True}
        if keyboard is None and ob_user.is_admin(for_buttons=True):
            reply_markup = self.sys_menu(_message)
        elif keyboard is not None:
            reply_markup = keyboard

        # HACK for some vendor who insert this shit to name of product or something
        if text is not None:
            text = str(text).replace("<sin", "sin")

        if type_send == "answer":
            return await _message.answer(text, reply_markup=reply_markup)
        elif type_send == "edit":
            # remove reply if edit message
            if not save_reply and 'reply_to_message' in _message and _message['reply_to_message'] is not None:
                res = await _message.answer(text, reply_markup=reply_markup)
                await self.delete(_message)
                return res
            elif 'text' not in _message or _message['text'] is None:
                res = await _message.answer(text, reply_markup=reply_markup)
                await self.delete(_message)
                return res

            return await _message.edit_text(text, reply_markup=reply_markup)
        elif type_send == "reply":
            try:
                return await _message.reply(text, reply_markup=reply_markup)
            except:
                return await _message.answer(text, reply_markup=reply_markup)
        elif type_send == "answer_photo":
            return await _message.answer_photo(photo=open(photo_path, 'rb'), caption=text, protect_content=True,
                                               reply_markup=reply_markup)
        elif type_send == "raw_photo":
            return await _message.answer_photo(photo=photo_path, caption=text, protect_content=True,
                                               reply_markup=reply_markup)

    async def delete(self, _message):
        from aiogram.utils.exceptions import MessageToDeleteNotFound, MessageCantBeDeleted
        try:
            return await _message.delete()
        except (MessageToDeleteNotFound, MessageCantBeDeleted):
            return False

    async def set_main_commands(self):
        await self.bot_instance.set_my_commands([
            self.start_command(as_bot_command=True),
            self.reports_command(as_bot_command=True),
            self.buy_command(as_bot_command=True),
            self.faq_command(as_bot_command=True),
            self.price_button(as_bot_command=True),
            self.news_button(as_bot_command=True),
            self.chat_button(as_bot_command=True),
            self.review_button(as_bot_command=True),
            self.support_button(as_bot_command=True),
        ])

    def sys_menu(self, message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[
            self.sys_actual_dates_button(), self.sys_bot_info_button(), self.sys_server_info()
        ])
        keyboard.add(*[
            self.sys_add_subscribe_button(), self.sys_send_message_button(), self.sys_server_restart_docker()
        ])
        return keyboard

    def get_user(self, message: types.Message):
        # TODO: create cache or something | from_user in inline button make from bot
        ob_user = User(message.chat)

        return ob_user

    def get_user_by_id(self, user_id):
        # TODO: create cache or something | from_user in inline button make from bot
        ob_user = User.init_from_id(user_id)

        return ob_user

    @staticmethod
    def format_datetime(date, with_time=False):
        if with_time:
            return date.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return date.strftime("%d/%m/%Y")

    def subscribe_string(self, subscribe, with_vendor=True, only_dates=False, with_last_date=False, with_expired=False):
        from subscription import Subscription
        text = ""
        if subscribe.exists():
            if with_vendor:
                vendor_title = subscribe.get_vendor_title()
                if vendor_title is not None:
                    text += "<b>" + vendor_title + "</b>: "

            sub_info = subscribe.get()

            if not only_dates:
                if subscribe.is_test():
                    text += "Тестовый доступ активен "
                else:
                    text += "Доступ активен "

            active_from = sub_info['ACTIVE_FROM']
            active_to = sub_info['ACTIVE_TO']

            if with_last_date:
                sub_copy = Subscription(subscribe.user, subscribe.vendor)
                last = sub_copy.get_last()
                if last is not None:
                    active_to = last['ACTIVE_TO']

            text += "(с {} по {})".format(
                self.format_datetime(active_from),
                self.format_datetime(active_to)
            )
        elif with_expired:
            if with_vendor:
                vendor_title = subscribe.get_vendor_title()
                if vendor_title is not None:
                    text += "<b>" + vendor_title + "</b>: "

            if not only_dates:
                text += "<b>Доступ не активен</b> "

            sub_info = subscribe.get(active=False)
            if sub_info is not None:
                active_to = sub_info['ACTIVE_TO']

                if with_last_date:
                    sub_copy = Subscription(subscribe.user, subscribe.vendor)
                    last = sub_copy.get_last(active=False)
                    if last is not None:
                        active_to = last['ACTIVE_TO']

                text += "(с {})".format(
                    self.format_datetime(active_to)
                )

        return text

    # endregion

    # region buttons
    @staticmethod
    def start_command(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/start", description="▶ Запустить бота")
        return types.KeyboardButton(text="▶ Запустить бота", callback_data="start")

    @staticmethod
    def reports_command(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/reports", description="📋 Отчеты")
        return types.KeyboardButton(text="📋 Отчеты", callback_data="reports")

    @staticmethod
    def buy_command(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/buy", description="💰 Купить доступ")
        return types.KeyboardButton(text="💰 Купить доступ", callback_data="buy")

    @staticmethod
    def faq_command(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/faq", description="⁉ FAQ")
        return types.KeyboardButton(text="⁉ FAQ", callback_data="FAQ")

    @staticmethod
    def price_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/price", description="💰 Стоимость подписки")
        return types.KeyboardButton(text="💰 Стоимость подписки", callback_data="PRICE")

    @staticmethod
    def news_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/news", description="📰 Новости")
        return types.KeyboardButton(text="📰 Новости", callback_data="NEWS")

    @staticmethod
    def chat_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/chat", description="💭 Группа")
        return types.KeyboardButton(text="💭 Группа", callback_data="CHAT")

    @staticmethod
    def review_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/review", description="📌 Оставить отзыв")
        return types.KeyboardButton(text="📌 Оставить отзыв", callback_data="REVIEW")

    @staticmethod
    def support_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/support", description="🗿 Тех. поддержка")
        return types.KeyboardButton(text="🗿 Тех. поддержка", callback_data="SUPPORT")

    @staticmethod
    def sys_send_message_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/sys_send", description="📣 Рассылка")
        return types.KeyboardButton(text="📣 Рассылка", callback_data="Рассылка")

    @staticmethod
    def sys_actual_dates_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/sys_actual_dates", description="Актуальные даты")
        return types.KeyboardButton(text="Актуальные даты", callback_data="Актуальные даты")

    @staticmethod
    def sys_bot_info_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/sys_bot_info", description="Сводная по боту")
        return types.KeyboardButton(text="Сводная по боту", callback_data="Сводная по боту")

    @staticmethod
    def sys_add_subscribe_button(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/sys_add_subscribe", description="Продлить подписку")
        return types.KeyboardButton(text="Продлить подписку", callback_data="Продлить подписку")

    @staticmethod
    def sys_server_info(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/sys_server_info", description="Сводная по серверу")
        return types.KeyboardButton(text="Сводная по серверу", callback_data="Сводная по серверу")

    @staticmethod
    def sys_server_restart_docker(as_bot_command=False):
        if as_bot_command:
            return types.BotCommand(command="/sys_server_restart_docker", description="Рестарт докера")
        return types.KeyboardButton(text="Рестарт докера", callback_data="Рестарт докера")

    # endregion
