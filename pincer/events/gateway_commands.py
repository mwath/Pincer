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

from dataclasses import dataclass
from enum import auto, Enum
from typing import List, Optional, Tuple, Union

from .presence import Activity
from ..objects.intents import Intents
from ..utils.api_object import APIObject
from ..utils.types import APINullable, MISSING
from ..utils.snowflake import Snowflake

@dataclass
class Identify(APIObject):
    """
    Used to trigger the initial handshake with the gateway.

    :param token:
        authentication token

    :param properties:
        connection properties

    :param compress:
        whether this connection supports compression of packets

    :param large_threshold:
        value between 50 and 250, total number
        of members where the gateway will stop sending offline
        members in the guild member list

    :param shard:
        used for Guild Sharding

    :param presence:
        presence structure for initial presence information

    :param intents:
        the Gateway Intents you wish to receive
    """
    token: str
    properties: dict[str, str]
    intents: Intents

    compress: APINullable[bool] = MISSING
    large_threshold: APINullable[int] = MISSING
    shard: APINullable[Tuple[int, int]] = MISSING
    presence: APINullable[...] = MISSING  # FIXME

@dataclass
class Resume(APIObject):
    """
    Used to replay missed events when a disconnected client resumes.

    :param token:
        session token

    :param session_id:
        session id

    :param seq:
        last sequence number received
    """
    token: str
    session_id: str
    seq: int

@dataclass
class RequestGuildMembers(APIObject):
    """
    Used to request all members for a guild or a list of guilds.

    :param guild_id:
        id of the guild to get members for

    :param query:
        string that username starts with, or an empty string
        to return all members

    :param limit:
        maximum number of members to send matching the `query`;
        a limit of `0` can be used with an empty string `query`
        to return all members

    :param presences:
        used to specify if we want the presences of the matches members

    :param user_ids:
        used to specify which users you wish to fetch

    :param nonce:
        nonce to identify the Guild Members Chunk response
    """
    guild_id: Snowflake
    limit: int

    query: APINullable[str] = MISSING
    presences: APINullable[bool] = MISSING
    user_ids: APINullable[Union[Snowflake, List[Snowflake]]] = MISSING
    nonce: APINullable[str] = MISSING

@dataclass
class UpdateVoiceState(APIObject):
    """
    Sent when a client wants to join, move,
    or disconnect from a voice channel.

    :param guild_id:
        id of the guild

    :param channel_id:
        id of the voice channel client
        wants to join (null if disconnecting)

    :param self_mute:
        is the client muted

    :param self_deaf:
        is the client deafened
    """
    guild_id: Snowflake
    self_mute: bool
    self_deaf: bool
    
    channel_id: Optional[Snowflake] = None

class StatusType(Enum):
    """
    :param online:
        Online

    :param dnd:
        Do Not Disturb

    :param idle:
        AFK

    :param invisible:
        Invisible and shown as offline

    :param offline:
        Offline
    """
    online = auto()
    dnd = auto()
    idle = auto()
    invisible = auto()
    offline = auto()

@dataclass
class UpdatePresence(APIObject):
    """
    Sent by the client to indicate a presence or status update.

    :param since:
        unix time (in milliseconds) of when the client went idle,
        or null if the client is not idle

    :param activities:
        the user's activities

    :param status:
        the user's new status

    :param afk:
        whether or not the client is afk
    """
    activities: List[Activity]
    status: StatusType
    afk: bool
    since: Optional[int] = None