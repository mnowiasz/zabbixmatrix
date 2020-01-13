import asyncio
import configparser
import re
import sys
from pathlib import Path

from nio import AsyncClient

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

    :return: Error (if there's anything wrong with the configfile or NONE if everyhing is alright)
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


def _format_message(zabbix_subject: str, zabbix_message: str) -> str:
    """
    :param zabbix_subject: The alert's subject
    :type zabbix_subject: str
    :param zabbix_message: The altert's message
    :type zabbix_message: str
    :return: a (HTTML) formatted message
    :rtype: str
    """

    return "<b>{}</b><br /><br/ >{}".format(zabbix_subject, zabbix_message.replace('\n', '<br />'), "{}\n\n{}").format(
        zabbix_subject, zabbix_message)


async def _send(client: AsyncClient, rooms, subject: str, message: str):
    for the_room_id in rooms:
        await client.room_send(room_id=the_room_id, message_type="m.room.message", content={
            "msgtype": "m.text",
            "body": _format_message(zabbix_subject=subject, zabbix_message=message)})

    await client.close()


async def zabbix2matrixmain():
    if len(sys.argv) != 4:
        print("Usage: {} <room(s)> <subject> <message>".format(sys.argv[0]))
        exit(1)

    the_rooms = re.split("[, ;]+", sys.argv[1].strip())
    the_alert = sys.argv[2]
    the_message = sys.argv[3]

    error = _read_config()

    if error:
        print(error)
        exit(1)

    client = AsyncClient(homeserver=_config_values[_config_string_url], user=_config_values[_config_string_username])
    await client.login(password=_config_values[_config_string_password])
    asyncio.get_event_loop().run_until_complete(_send(client, the_rooms, the_alert, the_message))


if __name__ == '__main__':
    zabbix2matrixmain()
