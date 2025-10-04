import re
from telethon import TelegramClient, events

# === CONFIGURATION ===
api_id = 23846407


api_hash = '9e69e06dca3c31af87ca39a4bdca75aa'

source_group_id =  [
    -4609257427,
    -1002682944548,    #xforce
    -1002283197621,    #priority
    
]

#bot_token = '8478953544:AAFo_UHzc8TRoURrEiIVSh8wNcGfcddiZBI' 

#target_peer = '@gammachk'
target_group_id = 1003146202628

client = TelegramClient('forwarder_session', api_id, api_hash)

"""target_peers = [
    '@APNA_FIRST_TARGET_USERNAME',  # Example Target 1 (Checker)
    '@APNA_SECOND_TARGET_USERNAME', # Example Target 2 (Backup)
    '@THIRD_TARGET_USERNAME',       # Example Target 3 (Private)
]"""
# === PATTERNS TO MATCH ===
card_patterns = [
    r'(\d{13,16})[| ]+(\d{1,2})[\/| ]+(\d{2,4})[| ]+(\d{3,4})',
    r'(\d{13,16})\s+(\d{1,2})/(\d{2,4})\s+(\d{3,4})',
    r'(\d{13,16})\s+(\d{3,4})\s+(\d{1,2})/(\d{2,4})',
]

def extract_card(text):
    for pattern in card_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) == 4:
                card_number, val1, val2, val3 = match
                if int(val1) <= 12:
                    month, year, cvv = val1, val2, val3
                else:
                    cvv, month, year = val1, val2, val3
                year = year if len(year) == 4 else '20' + year
                return f"/ho {card_number}|{month.zfill(2)}|{year}|{cvv}"

    card = re.search(r'Card:\s*(\d{13,16})', text)
    month = re.search(r'Exp\.?\s*month:\s*(\d{1,2})', text, re.IGNORECASE)
    year = re.search(r'Exp\.?\s*year:\s*(\d{2,4})', text, re.IGNORECASE)
    cvv = re.search(r'CVV:\s*(\d{3,4})', text)
    if card and month and year and cvv:
        c = card.group(1)
        m = month.group(1).zfill(2)
        y = year.group(1)
        y = y if len(y) == 4 else '20' + y
        v = cvv.group(1)
        return f"/ho {c}|{m}|{y}|{v}"

    generic_card = re.search(r'(\d{13,16})', text)
    cvv2 = re.search(r'CVV[:\-]?\s*(\d{3,4})', text, re.IGNORECASE)
    exp = re.search(r'(EXP|EXPIRE|Exp)[ :\-]*([0-9]{1,2})/([0-9]{2,4})', text, re.IGNORECASE)

    if generic_card and cvv2 and exp:
        card_num = generic_card.group(1)
        month = exp.group(2).zfill(2)
        year = exp.group(3)
        year = year if len(year) == 4 else '20' + year
        cvv = cvv2.group(1)
        return f"/ho {card_num}|{month}|{year}|{cvv}"

    return None

# === EVENT HANDLER ===
@client.on(events.NewMessage(chats=source_group_id))
async def handler(event):
    msg = event.raw_text
    formatted = extract_card(msg)
    if formatted:
        #await client.send_message(target_peer, formatted)
        await client.send_message(target_group_id, formatted)
        print(f"Forwarded: {formatted}")

# === START THE CLIENT ===
#client.start()
client.start() 

print("Bot is running and scanning for card formats...")
client.run_until_disconnected()