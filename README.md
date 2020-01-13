# zabbix2matrix
A small python script for sending zabbix alerts to matrix channels

To use it you have to do perform the following steps:

1. Register a new matrix account (or use an existing one). You can even
do this by curl (https://www.matrix.org/docs/guides/client-server-api)
2. Invite the account to the channels (public/private, whatever) where
you'd like to receive the alerts
3. Enter your credentials (inkcuding the URL to the homserver where you've
registered the matrix account) in a file named matrix.conf (see matrix.conf.example).
This file should go to the zabbix' homedirectory
4. Check the repo out as user zabbix and install zabbix2matrix by pip:
`pip install --user .` 
5. Create a symlink, so zabbix can use the script: ` ln -s /var/lib/zabbix/home/.local/bin/zabbix2matrix /var/lib/zabbix/alertscripts/` 
(YMMV on your installation)
6. Add a new Media Type in zabbix (call it for example Matrix). Type `Script`,
Scriptname `zabbix2matrix`, add three parameters: First `{ALERT.SENDTO}`, Second `{ALERT.SUBJECT}`,
Third `{ALERT.MESSAGE}`
7. After hat you can add to your user(s) the Matrix media. `Send to` is the ID (or alias) 
of the matrix channel(s) where you want to receive alerts. You can add more than one, seperated
by whitespaces or colons. However, you *have* to make sure that the zabbix user is able to
join the channel (by inviting it first). 

Have fun :-)

