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
from __future__ import annotations

import logging
from asyncio import iscoroutinefunction
from inspect import Signature
from typing import Optional, Dict, List

from pincer import __package__, Client
from pincer.exceptions import (
    CommandIsNotCoroutine, CommandAlreadyRegistered, TooManyArguments,
    InvalidArgumentAnnotation, CommandDescriptionTooLong
)
from pincer.objects.application_command import (
    ApplicationCommand, ApplicationCommandType, ClientCommandStructure,
    ApplicationCommandOption, ApplicationCommandOptionType
)
from pincer.utils.extraction import get_signature_and_params
from pincer.utils.insertion import should_pass_ctx
from pincer.utils.types import Coro

_log = logging.getLogger(__package__)

_options_type_link = {
    # TODO: Implement other types:
    Signature.empty: ApplicationCommandOptionType.STRING,
    str: ApplicationCommandOptionType.STRING,
    int: ApplicationCommandOptionType.INTEGER,
    bool: ApplicationCommandOptionType.BOOLEAN,
    float: ApplicationCommandOptionType.NUMBER
}


def command(
        name: Optional[str] = None,
        description: Optional[str] = "Description not set",
        enable_default: Optional[bool] = True
):
    # TODO: Fix docs

    def decorator(func: Coro):
        if not iscoroutinefunction(func):
            raise CommandIsNotCoroutine(
                f"Command with call `{func.__name__}` is not a coroutine, "
                "which is required for commands."
            )

        cmd = name or func.__name__

        # TODO: Perform name check on cmd with r"^[\w-]{1,32}$"

        if len(description) > 100:
            raise CommandDescriptionTooLong(
                f"Command `{cmd}` (`{func.__name__}`) its description exceeds "
                "the 100 character limit."
            )

        if reg := ChatCommandHandler.register.get(cmd):
            raise CommandAlreadyRegistered(
                f"Command `{cmd}` (`{func.__name__}`) has already been "
                f"registered by `{reg.call.__name__}`."
            )

        sig, params = get_signature_and_params(func)
        pass_context = should_pass_ctx(sig, params)

        if len(params) > (26 if pass_context else 25):
            raise TooManyArguments(
                f"Command `{cmd}` (`{func.__name__}`) can only have 25 "
                f"arguments (excluding the context and self) yet {len(params)} "
                "were provided!"
            )

        options: List[ApplicationCommandOption] = []

        for param in params:
            param_type = _options_type_link.get(sig[param].annotation)
            if not param_type:
                raise InvalidArgumentAnnotation(
                    f"Annotation `{sig[param].annotation}` on parameter "
                    f"`{param}` in command `{cmd}` (`{func.__name__}`) is not "
                    f"a valid type."
                )

            options.append(ApplicationCommandOption(
                type=param_type,
                name=name,
                description=description,
                # TODO: Check for Optional type
                required=True
            ))

        ChatCommandHandler.register[cmd] = ClientCommandStructure(
            call=func,
            app=ApplicationCommand(
                name=name,
                description=description,
                type=ApplicationCommandType.CHAT_INPUT,
                default_permission=enable_default,
                options=options
            )
        )
        _log.info(f"Registered command `{cmd}` to `{func.__name__}`.")

    return decorator


class ChatCommandHandler:
    register: Dict[str, ClientCommandStructure] = {}

    # TODO: Fix docs
    def __init__(self, client: Client):
        # TODO: Fix docs
        self.client = client
        self.commands: List[ApplicationCommand] = []
        print(
            f"{len(ChatCommandHandler.register.items())} commands registered.")

    async def __init_existing_commands(self):
        async with self.client.http as sess:
            res = await sess.get(f"applications/{self.client.bot.id}/commands")
            self.commands = list(map(ApplicationCommand.from_dict, res))

    async def initialize(self):
        # TODO: Fix docs
        await self.__init_existing_commands()