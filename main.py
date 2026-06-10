# ----------------------------------------------- #
# Plugin Name           : TradingView-Webhook-Bot #
# Author Name           : fabston                 #
# File Name             : main.py                 #
# ----------------------------------------------- #

import logging

from flask import Flask, jsonify, request

import config
from handler import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    whitelisted_ips = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    logger.info("Webhook request received from %s", client_ip)

    if client_ip not in whitelisted_ips:
        logger.warning("Rejected webhook request from non-whitelisted IP %s", client_ip)
        return jsonify({"message": "Unauthorized"}), 401

    try:
        data = request.get_json(silent=True)
        if not data:
            logger.warning(
                "Rejected webhook request from %s because payload is empty or invalid JSON",
                client_ip,
            )
            return jsonify({"message": "Invalid JSON payload"}), 400

        logger.info(
            "Webhook payload accepted for validation from %s with fields: %s",
            client_ip,
            sorted(data.keys()),
        )

        if data.get("key") != config.sec_key:
            logger.warning(
                "Rejected webhook request from %s because the security key did not match",
                client_ip,
            )
            return jsonify({"message": "Unauthorized"}), 401

        if "msg" not in data:
            logger.warning(
                "Rejected webhook request from %s because required field 'msg' is missing",
                client_ip,
            )
            return jsonify({"message": "Missing required field: msg"}), 400

        logger.info("Authorized webhook received from %s; dispatching alert", client_ip)
        send_alert(data)
        logger.info("Webhook from %s processed successfully", client_ip)
        return jsonify({"message": "Webhook received successfully"}), 200

    except Exception:
        logger.exception(
            "Unhandled error while processing webhook request from %s", client_ip
        )
        return jsonify({"message": "Error"}), 400


if __name__ == "__main__":
    from waitress import serve

    logger.info("Starting TradingView Webhook Bot on 0.0.0.0:8080")
    serve(app, host="0.0.0.0", port=8080)
