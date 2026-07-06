"""
###############################################################
#
# LOGGER
#
###############################################################
"""

from datetime import datetime

LOG = []


def write(message):

    now = datetime.now()

    text = f"[{now}] {message}"

    LOG.append(text)

    return text


def history():

    return LOG


def clear():

    LOG.clear()
