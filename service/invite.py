#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: invite.py
Author: Maria Kevin
Created: 2026-08-27
Description: Invite-link creation, join tracking, and expiry kicks.
"""

__author__ = "Maria Kevin"
__version__ = "0.1.0"


from datetime import datetime, timedelta
from typing import Optional, Tuple

from loguru import logger
from pyrogram import enums, errors
from pyrogram.client import Client
from pyrogram.types import Chat, ChatJoinRequest, Message

from app.exceptions import ChannelResolveError, InviteCreateError
from model import InviteLink, InviteLinkStatus
from repository import invite_link_repository

_ALLOWED_CHAT_TYPES = (enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP)

_RIGHTS_FAILURE_TEXT = (
    "⚠️ Missing Bot Rights\n\n"
    "Make this bot an administrator in that channel or group and grant "
    "Invite Users via Link and Ban Users. Then send the channel again."
)


def channel_open_url(channel_id: int) -> str:
    """Deep link to open a channel/supergroup (still works after invite revoke)."""
    internal = str(channel_id).removeprefix("-100")
    return f"https://t.me/c/{internal}"


class InviteService:
    async def resolve_channel(self, bot: Client, message: Message) -> Tuple[int, str]:
        """Resolve channel id and title from a forward or @username / chat id text.

        Raises:
            ChannelResolveError: When input is missing, invalid, or not a
                channel/supergroup the bot can access.
        """
        chat: Optional[Chat] = None

        if message.forward_from_chat is not None:
            fwd = message.forward_from_chat
            logger.bind(chat_id=fwd.id, chat_type=str(fwd.type)).info(
                "Resolving channel from forwarded chat"
            )
            try:
                chat = await bot.get_chat(fwd.id)
            except Exception as e:
                logger.bind(chat_id=fwd.id, error=str(e)).warning(
                    "Failed to get_chat for forwarded channel"
                )
                raise ChannelResolveError(
                    "❌ Channel Not Found\n\n"
                    "I could not access that forwarded chat. Forward a post "
                    "from the channel, or send its @username / chat id."
                ) from e
        else:
            text = (message.text or message.caption or "").strip()
            if not text:
                raise ChannelResolveError(
                    "❌ Channel Required\n\n"
                    "Forward a message from the channel, or send its "
                    "@username or numeric chat id."
                )
            identifier: int | str
            try:
                identifier = int(text)
            except ValueError:
                identifier = text
            logger.bind(identifier=identifier).info(
                "Resolving channel from text identifier"
            )
            try:
                chat = await bot.get_chat(identifier)
            except (
                errors.UsernameInvalid,
                errors.UsernameNotOccupied,
                errors.PeerIdInvalid,
                errors.ChannelInvalid,
                errors.ChannelPrivate,
                ValueError,
            ) as e:
                logger.bind(identifier=identifier, error=str(e)).warning(
                    "Failed to resolve channel identifier"
                )
                raise ChannelResolveError(
                    "❌ Channel Not Found\n\n"
                    "I could not find that channel. Check the @username or "
                    "chat id, or forward a message from it."
                ) from e
            except Exception as e:
                logger.bind(identifier=identifier, error=str(e)).error(
                    "Unexpected error resolving channel"
                )
                raise ChannelResolveError(
                    "❌ Channel Not Found\n\n"
                    "Something went wrong looking up that channel. Try again "
                    "with a forward, @username, or chat id."
                ) from e

        if chat.type not in _ALLOWED_CHAT_TYPES:
            logger.bind(chat_id=chat.id, chat_type=str(chat.type)).warning(
                "Resolved chat is not a channel or supergroup"
            )
            raise ChannelResolveError(
                "❌ Wrong Chat Type\n\n"
                "Please send a channel or supergroup (not a private chat or "
                "basic group)."
            )

        title = chat.title or str(chat.id)
        logger.bind(channel_id=chat.id, channel_title=title).info("Channel resolved")
        return chat.id, title

    async def ensure_bot_rights(self, bot: Client, channel_id: int) -> Optional[str]:
        """Check bot is admin with invite and restrict rights.

        Returns:
            None if rights are sufficient, otherwise a user-facing message
            describing what to grant.
        """
        me = bot.me or await bot.get_me()
        try:
            member = await bot.get_chat_member(channel_id, me.id)
        except Exception as e:
            logger.bind(channel_id=channel_id, error=str(e)).warning(
                "Failed to fetch bot chat member for rights check"
            )
            return _RIGHTS_FAILURE_TEXT

        privileges = member.privileges
        missing: list[str] = []
        if member.status != enums.ChatMemberStatus.ADMINISTRATOR or privileges is None:
            missing.extend(["Invite Users via Link", "Ban Users"])
        else:
            if not privileges.can_invite_users:
                missing.append("Invite Users via Link")
            if not privileges.can_restrict_members:
                missing.append("Ban Users")

        if missing:
            logger.bind(channel_id=channel_id, missing=missing).warning(
                "Bot missing required channel admin rights"
            )
            needed = ",\n\t".join(missing)
            return (
                "⚠️ Missing Bot Rights\n\n"
                f"Grant the bot these permissions in that channel or group: "
                f"{needed}. Then send the channel again."
            )

        logger.bind(channel_id=channel_id).info("Bot rights check passed")
        return None

    async def create_invite(
        self,
        bot: Client,
        channel_id: int,
        duration_seconds: int,
        created_by: int,
    ) -> InviteLink:
        """Create a single-use Telegram invite link and persist it as pending.

        Raises:
            InviteCreateError: When Telegram rejects link creation.
        """
        try:
            chat = await bot.get_chat(channel_id)
        except Exception as e:
            logger.bind(channel_id=channel_id, error=str(e)).error(
                "get_chat failed before invite create"
            )
            raise InviteCreateError(
                "❌ Invite Failed\n\n"
                "I could not access that channel to create a link. Check that "
                "the bot is still an admin, then try again."
            ) from e

        channel_title = chat.title or str(channel_id)
        try:
            link = await bot.create_chat_invite_link(
                channel_id,
                creates_join_request=True,
            )
        except Exception as e:
            logger.error(f"create_chat_invite_link failed: {e}", exc_info=True)
            raise InviteCreateError(
                "❌ Invite Failed\n\n"
                "Telegram could not create the invite link. Confirm the bot "
                "has Invite Users via Link, then try again."
            ) from e

        if link is None or not link.invite_link:
            logger.bind(channel_id=channel_id).error(
                "create_chat_invite_link returned empty link"
            )
            raise InviteCreateError(
                "❌ Invite Failed\n\n"
                "This chat only accepts join requests through its public "
                "link. Use a channel where invite links are allowed."
            )

        doc = await invite_link_repository.create(
            channel_id=channel_id,
            channel_title=channel_title,
            invite_link=link.invite_link,
            duration_seconds=duration_seconds,
            created_by=created_by,
            invite_link_name=link.name,
        )
        logger.bind(
            link_id=str(doc.id),
            channel_id=channel_id,
            duration_seconds=duration_seconds,
            created_by=created_by,
        ).info("Pending invite link created")
        return doc

    async def _revoke_invite_link(
        self, bot: Client, channel_id: int, invite_link_url: str
    ) -> None:
        """Revoke a single-use invite on Telegram so it cannot be reused."""
        try:
            r = await bot.revoke_chat_invite_link(channel_id, invite_link_url)
            logger.bind(channel_id=channel_id, invite_link=invite_link_url, r=r).info(
                "Invite link revoked after use"
            )
        except Exception as e:
            logger.bind(
                channel_id=channel_id,
                invite_link=invite_link_url,
                error=str(e),
            ).warning("Failed to revoke invite link after use")

    async def on_join_request(
        self, bot: Client, request: ChatJoinRequest
    ) -> Optional[InviteLink]:
        """Approve a join request for a pending invite and mark it active.

        Ignores requests that are not tied to a pending invite we created.
        Approves first, then persists membership so a failed approve does not
        leave an active invite without a channel member. Revokes the Telegram
        link after the first successful join so it cannot be reused.
        """
        invite = request.invite_link
        if invite is None or not invite.invite_link or request.from_user is None:
            return None

        invite_link_url = invite.invite_link
        user_id = request.from_user.id
        doc = await invite_link_repository.get_by_invite_link(invite_link_url)
        if doc is None:
            logger.bind(invite_link=invite_link_url, user_id=user_id).debug(
                "Join request ignored: invite link not in database"
            )
            return None
        if doc.status != InviteLinkStatus.pending:
            logger.bind(
                link_id=str(doc.id),
                status=doc.status.value,
                user_id=user_id,
            ).debug("Join request ignored: invite not pending")
            return None

        try:
            await request.approve()
        except Exception as e:
            logger.bind(
                link_id=str(doc.id),
                user_id=user_id,
                chat_id=request.chat.id if request.chat else None,
                error=str(e),
            ).error("Failed to approve join request")
            return None

        updated = await self.on_member_joined(invite_link_url, user_id)
        if updated is not None:
            await self._revoke_invite_link(bot, updated.channel_id, invite_link_url)
        return updated

    async def on_member_joined(
        self, invite_link_url: str, user_id: int
    ) -> Optional[InviteLink]:
        """Mark a pending invite as active when a member joins via that link."""
        doc = await invite_link_repository.get_by_invite_link(invite_link_url)
        if doc is None:
            logger.bind(invite_link=invite_link_url, user_id=user_id).debug(
                "Join ignored: invite link not in database"
            )
            return None
        if doc.status != InviteLinkStatus.pending:
            logger.bind(
                link_id=str(doc.id),
                status=doc.status.value,
                user_id=user_id,
            ).debug("Join ignored: invite not pending")
            return None

        joined_at = datetime.utcnow()
        expires_at = joined_at + timedelta(seconds=doc.duration_seconds)
        updated = await invite_link_repository.mark_joined(
            doc.id, user_id, joined_at, expires_at
        )
        logger.bind(
            link_id=str(doc.id),
            user_id=user_id,
            expires_at=expires_at.isoformat(),
        ).info("Invite marked active after join")
        return updated

    async def kick_expired(self, bot: Client) -> int:
        """Ban+unban members whose active invite membership has expired.

        Idempotent: already-left members are marked expired; other kick
        failures are logged and retried on the next run.
        """
        now = datetime.utcnow()
        expired = await invite_link_repository.list_expired_active(now)
        logger.bind(count=len(expired)).info("Running kick_expired sweep")
        kicked = 0

        for link in expired:
            prefix = (
                f"kick_expired link={link.id} channel={link.channel_id} "
                f"user={link.joined_user_id}"
            )
            if link.joined_user_id is None:
                await invite_link_repository.mark_expired(link.id)
                kicked += 1
                logger.bind(link_id=str(link.id)).warning(
                    "Active invite missing joined_user_id; marked expired"
                )
                continue

            try:
                await bot.ban_chat_member(link.channel_id, link.joined_user_id)
                await bot.unban_chat_member(link.channel_id, link.joined_user_id)
            except errors.UserNotParticipant:
                logger.bind(link_id=str(link.id), user_id=link.joined_user_id).info(
                    "Member already left; marking invite expired"
                )
            except Exception as e:
                logger.bind(
                    link_id=str(link.id),
                    channel_id=link.channel_id,
                    user_id=link.joined_user_id,
                    error=str(e),
                    prefix=prefix,
                ).error("Kick failed; will retry next run")
                continue

            await invite_link_repository.mark_expired(link.id)
            kicked += 1
            logger.bind(
                link_id=str(link.id),
                channel_id=link.channel_id,
                user_id=link.joined_user_id,
            ).info("Expired member kicked and invite marked expired")

        logger.bind(kicked=kicked, scanned=len(expired)).info(
            "kick_expired sweep finished"
        )
        return kicked


invite_service = InviteService()
