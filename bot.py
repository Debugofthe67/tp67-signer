import os
import subprocess
import telebot # run: pip install pyTelegramBotAPI
import requests

# 1. Setup (Use Environment Variables in Render for security)
TOKEN = os.getenv('TELEGRAM_TOKEN') # Get from @BotFather
CERT_PASS = "123456" # Your .p12 password

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['document'])
def handle_ipa(message):
    if message.document.file_name.endswith('.ipa'):
        bot.reply_to(message, "📥 Downloading your IPA...")
        
        # 2. Download the file from Telegram
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("input.ipa", 'wb') as f:
            f.write(downloaded_file)

        bot.edit_message_text("✍️ Signing with zsign...", message.chat.id, message.id + 1)

        # 3. RUN ZSIGN (The Magic Part)
        # Assumes cert.p12 and prov.mobileprovision are in your GitHub repo
        try:
            subprocess.run([
                "zsign", 
                "-k", "cert.p12", 
                "-p", CERT_PASS, 
                "-m", "prov.mobileprovision", 
                "-o", "signed.ipa", 
                "input.ipa"
            ], check=True)
            
            # 4. Upload to Catbox (Free File Host)
            bot.edit_message_text("☁️ Uploading to Catbox...", message.chat.id, message.id + 1)
            files = {'fileToUpload': open('signed.ipa', 'rb')}
            data = {'reqtype': 'fileupload', 'userhash': ''}
            response = requests.post('https://catbox.moe', files=files, data=data)
            ipa_url = response.text

            # 5. Send back the ITMS Link
            itms_link = f"itms-services://?action=download-manifest&url=https://your-site.com{ipa_url}"
            bot.reply_to(message, f"✅ Done!\n\nInstall Link:\n{itms_link}")
            
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

bot.polling()
