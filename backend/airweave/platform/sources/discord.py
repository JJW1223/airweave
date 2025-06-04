"""Module defining the Discord source connector."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from airweave.platform.auth.schemas import AuthType
from airweave.platform.decorators import source
from airweave.platform.entities.discord import (
    DiscordChannel,
    DiscordGuild,
    DiscordMember,
    DiscordMessage,
    DiscordRole,
    DiscordUser,
)
from airweave.platform.sources._base import BaseSource

logger = logging.getLogger(__name__)


@source(
    name="Discord",
    short_name="discord",
    auth_type=AuthType.oauth2,
    auth_config_class="DiscordAuthConfig",
    config_class="DiscordConfig",
    labels=["Chat", "Collaboration"],
)
class DiscordSource(BaseSource):
    """Discord source integration class for fetching data from Discord API."""

    def __init__(self, access_token: str) -> None:
        """Initialize Discord source with access token.

        Args:
            access_token (str): Discord OAuth2 access token
        """
        self.access_token = access_token
        self.base_url = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    async def get_user(self) -> Optional[DiscordUser]:
        """Get current authenticated user information.

        Returns:
            Optional[DiscordUser]: User object if successful, None otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/@me", headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return DiscordUser(
                            id=data["id"],
                            username=data["username"],
                            discriminator=data.get("discriminator"),
                            avatar_url=f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png"
                            if data.get("avatar")
                            else None,
                            is_bot=data.get("bot", False),
                            created_at=datetime.fromtimestamp(
                                ((int(data["id"]) >> 22) + 1420070400000) / 1000
                            ),
                        )
                    logger.error(f"Failed to get user info: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None

    async def get_guilds(self) -> List[DiscordGuild]:
        """Get all guilds (servers) the user has access to.

        Returns:
            List[DiscordGuild]: List of guild objects
        """
        guilds = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/@me/guilds", headers=self.headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get guilds: {response.status}")
                        return guilds

                    data = await response.json()
                    for guild_data in data:
                        guilds.append(
                            DiscordGuild(
                                id=guild_data["id"],
                                name=guild_data["name"],
                                icon_url=f"https://cdn.discordapp.com/icons/{guild_data['id']}/{guild_data['icon']}.png"
                                if guild_data.get("icon")
                                else None,
                                owner_id=guild_data["owner_id"],
                                member_count=None,  # Requires additional API call
                                created_at=datetime.fromtimestamp(
                                    ((int(guild_data["id"]) >> 22) + 1420070400000) / 1000
                                ),
                            )
                        )
        except Exception as e:
            logger.error(f"Error getting guilds: {str(e)}")
        return guilds

    async def get_channels(self, guild_id: Optional[str] = None) -> List[DiscordChannel]:
        """Get channels from a specific guild or all accessible channels.

        Args:
            guild_id (Optional[str]):
                ID of the guild to fetch channels from. If None, fetches all accessible channels.

        Returns:
            List[DiscordChannel]: List of channel objects
        """
        channels = []
        try:
            if guild_id:
                # Get channels for specific guild
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/guilds/{guild_id}/channels", headers=self.headers
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            for channel_data in data:
                                channels.append(
                                    DiscordChannel(
                                        id=channel_data["id"],
                                        name=channel_data["name"],
                                        guild_id=guild_id,
                                        channel_type=channel_data["type"],
                                        topic=channel_data.get("topic"),
                                        position=channel_data["position"],
                                        created_at=datetime.fromtimestamp(
                                            ((int(channel_data["id"]) >> 22) + 1420070400000) / 1000
                                        ),
                                    )
                                )
            else:
                # Get all accessible channels
                guilds = await self.get_guilds()
                for guild in guilds:
                    guild_channels = await self.get_channels(guild.id)
                    channels.extend(guild_channels)
        except Exception as e:
            logger.error(f"Error getting channels: {str(e)}")
        return channels

    async def get_messages(self, channel_id: str, limit: int = 100) -> List[DiscordMessage]:
        """Get messages from a specific channel.

        Args:
            channel_id (str): ID of the channel to fetch messages from
            limit (int, optional): Maximum number of messages to fetch. Defaults to 100.

        Returns:
            List[DiscordMessage]: List of message objects
        """
        messages = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/channels/{channel_id}/messages",
                    headers=self.headers,
                    params={"limit": limit},
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get messages: {response.status}")
                        return messages

                    data = await response.json()
                    for msg in data:
                        messages.append(
                            DiscordMessage(
                                id=msg["id"],
                                content=msg["content"],
                                author_id=msg["author"]["id"],
                                channel_id=channel_id,
                                guild_id=msg.get("guild_id"),
                                mentions=[m["id"] for m in msg.get("mentions", [])],
                                attachments=[a["url"] for a in msg.get("attachments", [])],
                                created_at=datetime.fromisoformat(
                                    msg["timestamp"].replace("Z", "+00:00")
                                ),
                                edited_at=datetime.fromisoformat(
                                    msg["edited_timestamp"].replace("Z", "+00:00")
                                )
                                if msg.get("edited_timestamp")
                                else None,
                                is_pinned=msg.get("pinned", False),
                                is_system=msg.get("type", 0) != 0,
                            )
                        )
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
        return messages

    async def get_roles(self, guild_id: str) -> List[DiscordRole]:
        """Get roles from a specific guild.

        Args:
            guild_id (str): ID of the guild to fetch roles from

        Returns:
            List[DiscordRole]: List of role objects
        """
        roles = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/guilds/{guild_id}/roles", headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for role_data in data:
                            roles.append(
                                DiscordRole(
                                    id=role_data["id"],
                                    name=role_data["name"],
                                    guild_id=guild_id,
                                    color=role_data["color"],
                                    position=role_data["position"],
                                    permissions=role_data["permissions"],
                                    mentionable=role_data["mentionable"],
                                    hoist=role_data["hoist"],
                                    created_at=datetime.fromtimestamp(
                                        ((int(role_data["id"]) >> 22) + 1420070400000) / 1000
                                    ),
                                )
                            )
        except Exception as e:
            logger.error(f"Error getting roles: {str(e)}")
        return roles

    async def get_members(self, guild_id: str, limit: int = 1000) -> List[DiscordMember]:
        """Get members from a specific guild.

        Args:
            guild_id (str): ID of the guild to fetch members from
            limit (int, optional): Maximum number of members to fetch. Defaults to 1000.

        Returns:
            List[DiscordMember]: List of member objects
        """
        members = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/guilds/{guild_id}/members",
                    headers=self.headers,
                    params={"limit": limit},
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for member_data in data:
                            members.append(
                                DiscordMember(
                                    id=f"{guild_id}:{member_data['user']['id']}",  # Composite key
                                    user_id=member_data["user"]["id"],
                                    guild_id=guild_id,
                                    nick=member_data.get("nick"),
                                    roles=member_data["roles"],
                                    joined_at=datetime.fromisoformat(
                                        member_data["joined_at"].replace("Z", "+00:00")
                                    ),
                                    premium_since=datetime.fromisoformat(
                                        member_data["premium_since"].replace("Z", "+00:00")
                                    )
                                    if member_data.get("premium_since")
                                    else None,
                                    is_pending=member_data.get("pending", False),
                                )
                            )
        except Exception as e:
            logger.error(f"Error getting members: {str(e)}")
        return members

    async def validate_connection(self) -> bool:
        """Validate if the connection is still valid.

        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            user = await self.get_user()
            return user is not None
        except Exception as e:
            logger.error(f"Error validating connection: {str(e)}")
            return False

    @classmethod
    async def create(cls, credentials: Dict[str, Any]) -> "DiscordSource":
        """Create a new Discord source instance.

        Args:
            credentials (Dict[str, Any]): Dictionary containing access_token

        Returns:
            DiscordSource: New Discord source instance
        """
        return cls(access_token=credentials["access_token"])
