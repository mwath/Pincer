# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2021 Pincer
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import logging
from asyncio import iscoroutinefunction
from inspect import getfullargspec
from typing import Optional, TypeVar, Callable, Coroutine, Any, Union, Dict

from pincer import __package__
from pincer._config import GatewayConfig, events
from pincer.core.dispatch import GatewayDispatch
from pincer.core.gateway import Dispatcher
from pincer.core.http import HTTPClient
from pincer.exceptions import InvalidEventName
from pincer.objects.user import User

_log = logging.getLogger(__package__)

Coro = TypeVar('Coro', bound=Callable[..., Coroutine[Any, Any, Any]])

_events: Dict[str, Optional[Union[str, Coro]]] = {}

for event in events:
    _events[event] = None
    _events[f"on_{event}"] = None


class Client(Dispatcher):
    """
    The main instance which the user will interact with.
    """

    def __init__(self, token: str):
        # TODO: Write docs
        # TODO: Implement intents
        super().__init__(
            token,
            handlers={
                0: self.event_handler
            }
        )

        self.http = HTTPClient(token, GatewayConfig.version)
        self.bot: Optional[User] = None
        _events["ready"] = self.__on_ready

    @staticmethod
    def event(coroutine: Coro):
        # TODO: Write docs
        if not iscoroutinefunction(coroutine):
            raise TypeError("Any event which is registered must be a coroutine "
                            "function")

        name: str = coroutine.__name__.lower()

        if not name.startswith("on_"):
            raise InvalidEventName(
                f"The event `{name}` its name must start with `on_`"
            )

        if _events.get(name) is not None:
            raise InvalidEventName(
                f"The event `{name}` has already been registered or is not "
                f"a event name."
            )

        _events[name] = coroutine
        return coroutine

    async def event_handler(self, _, payload: GatewayDispatch):
        # TODO: Write docs
        middleware: Optional[Union[Coro, str]] = _events.get(
            payload.event_name.lower()
        )

        if iscoroutinefunction(middleware):
            final_call, params = await middleware(payload)
        else:
            final_call, params = middleware, dict()

        final_call: str = final_call
        params: dict = params

        final_call_routine: Optional[Coro] = _events.get(final_call)

        if iscoroutinefunction(final_call_routine):
            kwargs = {}
            args = getfullargspec(final_call_routine).args
            if len(args) >= 1 and args[0] == "self":
                kwargs["self"] = self

            await final_call_routine(**kwargs)

    async def __on_ready(self, payload: GatewayDispatch):
        # TODO: Write docs
        self.bot = User.from_dict(payload.data.get("user"))
        return "on_ready", dict()


Bot = Client