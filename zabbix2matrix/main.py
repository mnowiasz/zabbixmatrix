import configparser
import sys
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
_config_string_rooms = "rooms"
_config_strings = (_config_string_username, _config_string_password, _config_string_url, _config_string_rooms)

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
        # Transform room string into a set
        room_set = set()
        for room in _config_values[_config_string_rooms].split(","):
            stripped = room.strip();
            room_set.add(stripped)
        _config_values[_config_string_rooms] = room_set;
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
    if len(sys.argv) != 3:
        print("Usage: {} <subject> <message>".format(sys.argv[0]))
        exit(1)

    the_alert = sys.argv[1]
    the_message = sys.argv[2]

    error = _read_config()

    if error:
        print(error)
        exit(1)

    client = None
    try:
        client = MatrixClient(_config_values[_config_string_url])
        token = client.login(username=_config_values[_config_string_username],
                             password=_config_values[_config_string_password])

        for room_id in _config_values[_config_string_rooms]:
            the_room = client.join_room(room_id)
            _send_message(the_room, the_alert, the_message)

        client.logout()
        exit(0)
    except errors.MatrixRequestError as me:
        print(me.content)
        exit(1)


if __name__ == '__main__':
    zabbix2matrixmain()
