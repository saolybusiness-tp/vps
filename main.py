import os
import re
import asyncio
import aiohttp
from aiohttp import web
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ==============================================================================
# 🤖 LY TOPUP — TELEGRAM USERBOT LISTENER (24/7 CLOUD AUTO-FORWARDER)
# ==============================================================================

API_ID = int(os.environ.get("TELEGRAM_API_ID", "37057416"))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "f39bde739202ac9ab5d9b2f8a7dfa952")
SESSION_STRING = os.environ.get(
    "TELEGRAM_SESSION_STRING", 
    "1BVtsOI0Bu5FqEyCxgyVao6__djNmWd9I60MAGKyyhFAvkJ5fzgxQVNqm6rGiApxNeIrlNWY_WBvJoHweoVXVS8aTlDz5B413B5IerQW-nk1NlUE6sCJA7y2cEyheOKLmfNiLjdMMi3j5FlTp0xKIH9OyqlG6pEkLMdkXADUv8xjHWAaaHN-aKsAAGaLX8B3w7tNbkmkJXvzyx3cFx9JOxdOH2zvOutm0tM4wc8_CU4BPWFwZBVlLlDtUzwB-rB1kNp8xMBwgRvEmpQaQ2QGYKnKSJFpRp1lt2WtQd9i6PF26uwdovaPkA28GObEE0KnXpSnb7Cb9wgLnwZl3LKmbNwsNVfFpaBA="
).strip()

# Target Group ID: -5475606520
TARGET_GROUP_ID = int(os.environ.get("TARGET_GROUP_ID", "-5475606520"))

# Cloudflare Worker Webhook URL
WORKER_WEBHOOK_URL = os.environ.get(
    "WORKER_WEBHOOK_URL", 
    "https://ly-api.saoly-business.workers.dev/api/telegram/webhook"
)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage)
async def handle_incoming_message(event):
    chat_id = event.chat_id
    if chat_id != TARGET_GROUP_ID and str(chat_id) != str(TARGET_GROUP_ID):
        return

    message = event.message
    text = message.text or message.message or ""
    
    is_aba_payment = bool(re.search(
        r"paid\s*by|received\s*payment|merchant|aba\s*bank|payway|ត្រូវបានបង់ដោយ|aba\s*khqr|លេខប្រតិបត្តិការ|trx\.\s*id|apv",
        text, 
        re.IGNORECASE
    ))

    if not is_aba_payment:
        return

    print(f"\n⚡ [ABA PAYMENT DETECTED] ស្ទាក់ចាប់បានសារបង់ប្រាក់:")
    print(f"📝 {text[:100]}...\n")

    payload = {
        "update_id": event.id,
        "message": {
            "message_id": event.id,
            "from": {
                "id": message.sender_id or 0,
                "first_name": "ABA Auto-Forwarder",
                "is_bot": False
            },
            "chat": {
                "id": TARGET_GROUP_ID,
                "type": "group"
            },
            "date": int(message.date.timestamp()) if message.date else 0,
            "text": text
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                WORKER_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                res_data = await response.text()
                print(f"🚀 [WORKER RESPONSE] HTTP {response.status}: {res_data}")
    except Exception as err:
        print(f"❌ [WEBHOOK ERROR] បរាជ័យក្នុងការបាញ់ទៅ Worker: {err}")

async def health_check(request):
    return web.json_response({
        "status": "ONLINE",
        "service": "LY TOPUP Telegram Listener",
        "target_group": TARGET_GROUP_ID,
        "worker_target": WORKER_WEBHOOK_URL
    })

async def main():
    print("==================================================")
    print("🚀 LY TOPUP Telegram Listener កំពុងចាប់ផ្តើម...")
    print(f"🔑 API ID: {API_ID}")
    print(f"🎯 Target Group: {TARGET_GROUP_ID}")
    print(f"🌐 Worker URL: {WORKER_WEBHOOK_URL}")
    print("==================================================")
    
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Health Check Web Server កំពុងដំណើរការលើ Port {port}")

    await client.start()
    me = await client.get_me()
    print(f"✅ បាន Login ជោគជ័យជា៖ {me.first_name} (@{me.username})")
    print("📡 Listener កំពុងរង់ចាំស្ទាក់ចាប់សារ ABA ២៤/៧...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
