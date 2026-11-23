"""Подключает бота к Vercel. Запуск:
python set_webhook.py <BOT_TOKEN> https://<проект>.vercel.app <WEBHOOK_SECRET>
"""
import sys, json, urllib.parse, urllib.request

if len(sys.argv) < 3:
    sys.exit(__doc__)
token, base = sys.argv[1], sys.argv[2].rstrip("/")
secret = sys.argv[3] if len(sys.argv) > 3 else ""
params = {"url": base + "/api/webhook", "allowed_updates": json.dumps(["message", "callback_query"])}
if secret:
    params["secret_token"] = secret
url = f"https://api.telegram.org/bot{token}/setWebhook?" + urllib.parse.urlencode(params)
print(urllib.request.urlopen(url).read().decode())
print(urllib.request.urlopen(f"https://api.telegram.org/bot{token}/getWebhookInfo").read().decode())
