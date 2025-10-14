import re
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession 

# === CONFIGURATION (SAB KUCH RAILWAY VARIABLES SE UTHTHA HAI) ===
try:
    # 1. API Credentials (Ye same reh sakte hain, ya alag bhi de sakte ho)
    API_ID = int(os.environ.get("API_ID"))
    API_HASH = os.environ.get("API_HASH")
    
    # 2. STRING SESSION (Is Service ke liye ALAG Session String chahiye!)
    SESSION_STRING = os.environ.get("PROXY_STRING_SESSION") 
    
    # 3. Source and Target IDs (ALAG se set karna)
    PROXY_SOURCE_IDS_STR = os.environ.get("PROXY_SOURCE_IDS")
    PROXY_TARGET_ID = int(os.environ.get("PROXY_TARGET_ID")) 
    
    # Source IDs ko string se list of integers mein convert kiya
    source_group_ids = [int(i.strip()) for i in PROXY_SOURCE_IDS_STR.split(',') if i.strip()]
    
except Exception as e:
    print(f"FATAL ERROR: Environment variable setting mein gadbad hai, bro! {e}")
    print("Zaroor check karo: API_ID, API_HASH, PROXY_STRING_SESSION, PROXY_SOURCE_IDS, PROXY_TARGET_ID.")
    exit(1)

# Sanity check
if not all([API_ID, API_HASH, SESSION_STRING, source_group_ids, PROXY_TARGET_ID]):
    print("FATAL ERROR: Koi zaroori Environment Variable set nahi hai. Sab set karo.")
    exit(1) 


# === PROXY EXTRACTION LOGIC (Har Type Ki Proxy Ke Liye) ===

def extract_proxy(text):
    # Pattern 1: IP:PORT (Simplest and most common)
    pattern1 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b' 
    
    # Pattern 2: IP:PORT:USER:PASS (Auth proxy)
    pattern2 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}:\S+:\S+\b'
    
    # Pattern 3: USER:PASS@IP:PORT (Common for HTTP/Socks clients)
    pattern3 = r'\b\S+:\S+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b'
    
    # Pattern 4: SOCKS5/SOCKS4 proxy format (e.g., socks5: 1.1.1.1:8080)
    pattern4 = r'(socks4|socks5):\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'

    # Pattern 5: IP|PORT|USER|PASS (Pipe separated format)
    pattern5 = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\|(\d{2,5})\|(\S+)\|(\S+)'
    
    # Pattern 6: IP;PORT;USER;PASS (Semicolon separated)
    pattern6 = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3});(\d{2,5});(\S+);(\S+)'
    
    # Priority order: Complex (auth/structured) first, then simple IP:PORT
    for pattern in [pattern3, pattern2, pattern5, pattern6, pattern4, pattern1]:
        # re.IGNORECASE use kiya for socks4/socks5
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Formatting the output for clarity
            if pattern in [pattern5, pattern6]:
                # Structured formats
                return f"SCRAPED PROXY: {match.group(1)}:{match.group(2)}:{match.group(3)}:{match.group(4)}"
            elif pattern == pattern4:
                # SOCKS format
                return f"SCRAPED PROXY ({match.group(1).upper()}): {match.group(2)}:{match.group(3)}"
            else:
                # Direct match
                return f"SCRAPED PROXY: {match.group(0)}"
            
    return None


# === TELETHON CLIENT AND HANDLER ===

# Client initialization (alag session string use ho raha hai)
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


@client.on(events.NewMessage(chats=source_group_ids))
async def handler(event):
    msg = event.raw_text
    
    formatted_proxy = extract_proxy(msg)
    
    if formatted_proxy:
        await client.send_message(PROXY_TARGET_ID, formatted_proxy)
        print(f"Forwarded Proxy: {formatted_proxy}")

# === START THE CLIENT ===
with client:
    print("Proxy Scraper Bot is running and ready for fast extraction...")
    client.run_until_disconnected()