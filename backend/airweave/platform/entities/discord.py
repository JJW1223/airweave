"""Discord entity schemas for Airweave platform."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from airweave.platform.entities._base import BaseEntity, EntityType


class DiscordUser(BaseEntity):
    """Discord user entity."""

    type: EntityType = Field(EntityType.USER, description="Type of the entity (user)")
    username: str = Field(..., description="Discord username")
    discriminator: Optional[str] = Field(None, description="Discord user discriminator (legacy)")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar")
    is_bot: bool = Field(False, description="Whether the user is a bot")
    created_at: datetime = Field(..., description="When the user was created")


class DiscordGuild(BaseEntity):
    """Discord server (guild) entity."""

    type: EntityType = Field(
        EntityType.ORGANIZATION, description="Type of the entity (organization)"
    )
    name: str = Field(..., description="Guild name")
    icon_url: Optional[str] = Field(None, description="URL to guild's icon")
    owner_id: str = Field(..., description="ID of the guild owner")
    member_count: Optional[int] = Field(None, description="Number of members in the guild")
    created_at: datetime = Field(..., description="When the guild was created")


class DiscordChannel(BaseEntity):
    """Discord channel entity."""

    type: EntityType = Field(EntityType.CHANNEL, description="Type of the entity (channel)")
    name: str = Field(..., description="Channel name")
    guild_id: str = Field(..., description="ID of the guild this channel belongs to")
    channel_type: int = Field(
        ..., description="Type of the channel (0: text, 1: DM, 2: voice, etc.)"
    )
    topic: Optional[str] = Field(None, description="Channel topic/description")
    position: int = Field(..., description="Sorting position of the channel")
    created_at: datetime = Field(..., description="When the channel was created")


class DiscordMessage(BaseEntity):
    """Discord message entity."""

    type: EntityType = Field(EntityType.MESSAGE, description="Type of the entity (message)")
    content: str = Field(..., description="Message content")
    author_id: str = Field(..., description="ID of the message author")
    channel_id: str = Field(..., description="ID of the channel where the message was sent")
    guild_id: Optional[str] = Field(
        None, description="ID of the guild where the message was sent (if any)"
    )
    mentions: List[str] = Field(
        default_factory=list, description="List of user IDs mentioned in the message"
    )
    attachments: List[str] = Field(default_factory=list, description="List of attachment URLs")
    created_at: datetime = Field(..., description="When the message was created")
    edited_at: Optional[datetime] = Field(None, description="When the message was last edited")
    is_pinned: bool = Field(False, description="Whether the message is pinned")
    is_system: bool = Field(False, description="Whether this is a system message")


class DiscordRole(BaseEntity):
    """Discord role entity."""

    type: EntityType = Field(EntityType.ROLE, description="Type of the entity (role)")
    name: str = Field(..., description="Role name")
    guild_id: str = Field(..., description="ID of the guild this role belongs to")
    color: int = Field(..., description="Role color as integer")
    position: int = Field(..., description="Sorting position of the role")
    permissions: int = Field(..., description="Role permissions as integer")
    mentionable: bool = Field(False, description="Whether the role is mentionable")
    hoist: bool = Field(
        False, description="Whether the role is displayed separately in the member list"
    )
    created_at: datetime = Field(..., description="When the role was created")


class DiscordMember(BaseEntity):
    """Discord guild member entity."""

    type: EntityType = Field(EntityType.MEMBER, description="Type of the entity (member)")
    user_id: str = Field(..., description="ID of the user")
    guild_id: str = Field(..., description="ID of the guild")
    nick: Optional[str] = Field(None, description="Nickname of the member in the guild")
    roles: List[str] = Field(default_factory=list, description="List of role IDs the member has")
    joined_at: datetime = Field(..., description="When the member joined the guild")
    premium_since: Optional[datetime] = Field(
        None, description="When the member started boosting the guild"
    )
    is_pending: bool = Field(
        False, description="Whether the member has not yet passed the guild's membership screening"
    )
