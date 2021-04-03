# Relay-Bot

A bot that can relay messages between channels on different Discord servers

# Installation
1. `git clone https://github.com/hurek/relay-bot.git`
2. `cd relay-bot`
2. Install requirements from `requirements.txt` for `Python 3` with `pip3 install -r requirements.txt`
3. Go to [Discord Developers portal](https://discord.com/developers/) and create new Application. Official instructions [here](https://discordpy.readthedocs.io/en/latest/discord.html).
4. `mv configExample.py config.py` and copy your bot token from the dashboard here.
5. `cd /etc/systemd/system`
6. `sudo nano relay-bot.service`
7. Copy and paste following settings:
```
[Unit]
Description=Telegram bot 'Relay Bot'
After=syslog.target
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/PATH_TO_BOT_DIRECTORY/relay-bot
ExecStart=/usr/bin/python3 /PATH_TO_BOT_DIRECTORY/relay-bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
8. Save file and run following commands to enable bot service:
```
sudo systemctl daemon-reload
sudo systemctl start relay-bot.service
sudo systemctl status relay-bot.service
```
9. Go to Application dashboard -> OAuth2 and check the box for **Bot**.
10. Set following permissions for Bot:
* Manage Webhooks
* View Channels
* Send Messages
* Embed Links
* Attach Files
* Read Message History
* Mention Everyone
* Use External Emojis
11. Copy invitation link to your browser, add bot to your server.
12. Send `!relay.help` to see list of Bot commands. 
