"""
###############################################################
#
# SYNAPSE ENGINE
# VERSION INFORMATION
#
###############################################################
"""

APP_NAME = "SYNAPSE"

APP_VERSION = "1.0.0"

ENGINE_VERSION = "1.0"

AUTHOR = "Mon101sanprakob"

SLOGAN = "อยู่นิ้งๆไม่เจ็บตัว"

DESCRIPTION = """
SYNAPSE
Sound & Visual Therapy

Mathematical Analysis Engine
Golden Ratio
Moon Cycle
Calendar
Lunar Phase
Energy Index

"""

COPYRIGHT = "Copyright © SYNAPSE"

BUILD = "001"

STATUS = "Development"

DEBUG = True


def version():

    return f"{APP_NAME} {APP_VERSION}"


def engine():

    return ENGINE_VERSION


def info():

    return {

        "app":APP_NAME,

        "version":APP_VERSION,

        "engine":ENGINE_VERSION,

        "author":AUTHOR,

        "status":STATUS,

        "build":BUILD

}
