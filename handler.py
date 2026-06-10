# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : handler.py              #
# ----------------------------------------------- #

import logging
import smtplib
import ssl
from email.mime.text import MIMEText

import tweepy
from discord_webhook import DiscordEmbed, DiscordWebhook
from slack_webhook import Slack
from telegram import Bot

import config

logger = logging.getLogger(__name__)


def _sanitize_alert_message(message):
    return message.replace("*", "").replace("_", "").replace("`", "")


def send_alert(data):
    msg = data["msg"].encode("latin-1", "backslashreplace").decode("unicode_escape")
    logger.info("Starting alert dispatch with message length %s", len(msg))

    if config.send_telegram_alerts:
        target_channel = data.get("telegram", config.channel)
        target_source = "payload-provided" if "telegram" in data else "configured"
        logger.info(
            "Telegram alerts enabled; sending notification to %s channel %s",
            target_source,
            target_channel,
        )
        try:
            tg_bot = Bot(token=config.tg_token)
            tg_bot.sendMessage(
                target_channel,
                msg,
                parse_mode="MARKDOWN",
            )
            logger.info(
                "Telegram notification sent successfully to %s channel %s",
                target_source,
                target_channel,
            )
        except Exception:
            logger.exception(
                "Telegram notification failed for %s channel %s",
                target_source,
                target_channel,
            )
    else:
        logger.debug("Telegram alerts disabled; skipping Telegram notification")

    if config.send_discord_alerts:
        webhook_path = data.get("discord", config.discord_webhook)
        target_source = "payload-provided" if "discord" in data else "configured"
        logger.info(
            "Discord alerts enabled; sending notification using %s webhook",
            target_source,
        )
        try:
            webhook = DiscordWebhook(
                url="https://discord.com/api/webhooks/" + webhook_path
            )
            embed = DiscordEmbed(title=msg)
            webhook.add_embed(embed)
            webhook.execute()
            logger.info(
                "Discord notification sent successfully using %s webhook", target_source
            )
        except Exception:
            logger.exception(
                "Discord notification failed using %s webhook", target_source
            )
    else:
        logger.debug("Discord alerts disabled; skipping Discord notification")

    if config.send_slack_alerts:
        webhook_path = data.get("slack", config.slack_webhook)
        target_source = "payload-provided" if "slack" in data else "configured"
        logger.info(
            "Slack alerts enabled; sending notification using %s webhook", target_source
        )
        try:
            slack = Slack(url="https://hooks.slack.com/services/" + webhook_path)
            slack.post(text=msg)
            logger.info(
                "Slack notification sent successfully using %s webhook", target_source
            )
        except Exception:
            logger.exception(
                "Slack notification failed using %s webhook", target_source
            )
    else:
        logger.debug("Slack alerts disabled; skipping Slack notification")

    if config.send_twitter_alerts:
        logger.info("Twitter alerts enabled; sending status update")
        try:
            tw_auth = tweepy.OAuthHandler(config.tw_ckey, config.tw_csecret)
            tw_auth.set_access_token(config.tw_atoken, config.tw_asecret)
            tw_api = tweepy.API(tw_auth)
            tw_api.update_status(status=_sanitize_alert_message(msg))
            logger.info("Twitter status update sent successfully")
        except Exception:
            logger.exception("Twitter status update failed")
    else:
        logger.debug("Twitter alerts disabled; skipping Twitter status update")

    if config.send_email_alerts:
        logger.info(
            "Email alerts enabled; sending notification to %s recipient(s)",
            len(config.email_receivers),
        )
        try:
            email_msg = MIMEText(_sanitize_alert_message(msg))
            email_msg["Subject"] = config.email_subject
            email_msg["From"] = config.email_sender
            email_msg["To"] = config.email_sender
            context = ssl.create_default_context()
            logger.info(
                "Connecting to email server %s:%s", config.email_host, config.email_port
            )
            with smtplib.SMTP_SSL(
                config.email_host, config.email_port, context=context
            ) as server:
                server.login(config.email_user, config.email_password)
                logger.info("Authenticated to email server")
                server.sendmail(
                    config.email_sender, config.email_receivers, email_msg.as_string()
                )
                server.quit()
            logger.info("Email notification sent successfully")
        except Exception:
            logger.exception("Email notification failed")
    else:
        logger.debug("Email alerts disabled; skipping email notification")

    logger.info("Alert dispatch finished")
