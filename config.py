# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : config.py               #
# ----------------------------------------------- #

import os


def _get_env(name, default=""):
    return os.getenv(name, default)


def _get_bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _get_int_env(name, default=0):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return int(value)


def _get_list_env(name, default=None):
    value = os.getenv(name)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


def _validate_required_env(alert_name, required_variables):
    missing_variables = [
        variable
        for variable in required_variables
        if os.getenv(variable) is None or os.getenv(variable).strip() == ""
    ]
    if missing_variables:
        raise ValueError(
            f"{alert_name} alerts are enabled, but the following required "
            f"environment variables are not set: {', '.join(missing_variables)}"
        )


# TradingView Example Alert Message:
# {
# "key":"9T2q394M92", "telegram":"-1001298977502", "discord":"789842349670960670/BFeBBrCt-w2Z9RJ2wlH6TWUjM5bJuC29aJaJ5OQv9sE6zCKY_AlOxxFwRURkgEl852s3", "msg":"Long #{{ticker}} at `{{close}}`"
# }

sec_key = _get_env(
    "SEC_KEY", ""  # Can be anything. Has to match with "key" in your TradingView alert message
)

# Telegram Settings
send_telegram_alerts = _get_bool_env("SEND_TELEGRAM_ALERTS", False)
if send_telegram_alerts:
    _validate_required_env("Telegram", ("TG_TOKEN", "CHANNEL"))
tg_token = _get_env("TG_TOKEN", "")  # Bot token. Get it from @Botfather
channel = _get_int_env("CHANNEL", 0)  # Channel ID (ex. -1001487568087)

# Discord Settings
send_discord_alerts = _get_bool_env("SEND_DISCORD_ALERTS", False)
if send_discord_alerts:
    _validate_required_env("Discord", ("DISCORD_WEBHOOK",))
discord_webhook = _get_env(
    "DISCORD_WEBHOOK", ""
)  # Discord Webhook URL (https://support.discordapp.com/hc/de/articles/228383668-Webhooks-verwenden)

# Slack Settings
send_slack_alerts = _get_bool_env("SEND_SLACK_ALERTS", False)
if send_slack_alerts:
    _validate_required_env("Slack", ("SLACK_WEBHOOK",))
slack_webhook = _get_env(
    "SLACK_WEBHOOK", ""
)  # Slack Webhook URL (https://api.slack.com/messaging/webhooks)

# Twitter Settings
send_twitter_alerts = _get_bool_env("SEND_TWITTER_ALERTS", False)
if send_twitter_alerts:
    _validate_required_env(
        "Twitter", ("TW_CKEY", "TW_CSECRET", "TW_ATOKEN", "TW_ASECRET")
    )
tw_ckey = _get_env("TW_CKEY", "")
tw_csecret = _get_env("TW_CSECRET", "")
tw_atoken = _get_env("TW_ATOKEN", "")
tw_asecret = _get_env("TW_ASECRET", "")

# Email Settings
send_email_alerts = _get_bool_env("SEND_EMAIL_ALERTS", False)
if send_email_alerts:
    _validate_required_env(
        "Email",
        (
            "EMAIL_SENDER",
            "EMAIL_RECEIVERS",
            "EMAIL_SUBJECT",
            "EMAIL_PORT",
            "EMAIL_HOST",
            "EMAIL_USER",
            "EMAIL_PASSWORD",
        ),
    )
email_sender = _get_env("EMAIL_SENDER", "")  # Your email address
email_receivers = _get_list_env("EMAIL_RECEIVERS", [])  # Receivers, can be multiple
email_subject = _get_env("EMAIL_SUBJECT", "Trade Alert!")

email_port = _get_int_env("EMAIL_PORT", 465)  # SMTP SSL Port (ex. 465)
email_host = _get_env("EMAIL_HOST", "")  # SMTP host (ex. smtp.gmail.com)
email_user = _get_env("EMAIL_USER", "")  # SMTP Login credentials
email_password = _get_env("EMAIL_PASSWORD", "")  # SMTP Login credentials
