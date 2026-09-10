You need two values: the bot token and your chat ID.

1. In Telegram, search for **@BotFather**.
2. Send `/newbot`, choose a name and username.
3. BotFather will show a token like:

```text
123456789:AAExampleSecretToken
```

Copy this as `MASCLOUD_TELEGRAM_BOT_TOKEN`. Keep it private.

4. Open your newly created bot in Telegram and press **Start** (or send `hello`).
5. In PowerShell, run:

```powershell
$env:MASCLOUD_TELEGRAM_BOT_TOKEN = "paste-token-here"
$updates = Invoke-RestMethod -Uri "https://api.telegram.org/bot$env:MASCLOUD_TELEGRAM_BOT_TOKEN/getUpdates"
$updates.result[-1].message.chat.id
```

The number printed is your `MASCLOUD_TELEGRAM_CHAT_ID`.

Then launch the monitor:

```powershell
$env:MASCLOUD_TELEGRAM_CHAT_ID = "paste-chat-id-here"
python app.py
```

If the chat-ID command returns nothing, send another normal message to your bot first, then run it again.