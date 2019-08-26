import configparser
import sys
import re

from pathlib import Path

from matrix_client import errors
from matrix_client.client import MatrixClient
from matrix_client.room import Room

_config_directories = ("/var/lib/zabbix", Path.home(), Path.cwd())
_config_filename = "matrix.conf"
_config_string_section = "matrix"
_config_string_username = "username"
_config_string_password = "password"
_config_string_url = "url"
_config_strings = (_config_string_username, _config_string_password, _config_string_url)

_config_values = {}


def _read_config() -> str:
    """

    :return: Error (if there'S anything wrong with the configfile or NONE)
    :rtype: String
    """

    # Try to find a config file

    for path in _config_directories:
        configfile = (Path(path) / _config_filename).resolve()
        if configfile.is_file():
            break
    else:
        # looped, no configfile found
        configfile = None

    if not configfile:
        return "Unable to find configfile"

    _parser = configparser.ConfigParser()
    _parser.read(configfile)
    try:
        for value in _config_strings:
            _config_values[value] = _parser[_config_string_section][value]
            if _config_values[value] is None or len(_config_values[value]) == 0:
                return "Empty value for " + value
    except KeyError as key_error:
        missing_key = key_error.args[0]
        return missing_key + " not set!"


def _send_message(the_room: Room, zabbix_subject: str, zabbix_message: str):
    """

    :param the_room: The room the message is being send to
    :type the_room: Room
    :param zabbix_subject: Zabbix subject
    :type zabbix_subject: str
    :param zabbix_message: Zabbix's message
    :type zabbix_message: str
    :return:
    :rtype:

    Sends the alerts to the room
    """

    the_room.send_html(
        "<b>{}</b><br><br>{}".format(zabbix_subject, zabbix_message, "{}\n\n{}").format(zabbix_subject, zabbix_message))


def zabbix2matrixmain():
    if len(sys.argv) != 4:
        print("Usage: {} <room(s)> <subject> <message>".format(sys.argv[0]))
        exit(1)

    the_rooms = re.split("[, \-;,]+", sys.argv[1].strip())
    the_alert = sys.argv[2]
    the_message = sys.argv[3]

    error = _read_config()

    if error:
        print(error)
        exit(1)

    client = None
    try:
        client = MatrixClient(_config_values[_config_string_url])
        token = client.login(username=_config_values[_config_string_username],
                             password=_config_values[_config_string_password])

        for room_id in the_rooms:
            the_room = client.join_room(room_id)
            _send_message(the_room, the_alert, the_message)

        client.logout()
        exit(0)
    except errors.MatrixRequestError as me:
        print(me.content)
        exit(1)


if __name__ == '__main__':
    zabbix2matrixmain()
