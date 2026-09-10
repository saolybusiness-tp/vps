"""
LY TOPUP — GENERATE TELEGRAM SESSION STRING
===========================================
រត់ script នេះម្តងគត់ (ក្នុង Google Colab ឬកុំព្យូទ័រ) ដើម្បីទាញយក Session String!
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 10672540
API_HASH = "d05228f6282730bdffdfe02898fa7de5"

print("==================================================")
print("🔑 LY TOPUP — TELEGRAM SESSION GENERATOR")
print("==================================================")

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    session_string = client.session.save()
    print("\n" + "="*60)
    print("🎉 អបអរសាទរ! នេះជា TELEGRAM_SESSION_STRING របស់អ្នក៖")
    print("="*60)
    print(session_string)
    print("="*60)
    print("\n👉 សូម Copy អក្សរខាងលើនេះ យកទៅដាក់លើ Cloud (Render/Koyeb)!")
