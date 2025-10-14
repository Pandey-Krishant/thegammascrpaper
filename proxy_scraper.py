import re
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession 

# === CONFIGURATION (Railway Build Fixes) ===
# API IDs are hardcoded to avoid the "secret not found" build errors.
API_ID = 23846407
API_HASH = '9e69e06dca3c31af87ca39a4bdca75aa' 

try:
    # Saare zaroori variables Environment se uthenge
    SESSION_STRING = os.environ.get("PROXY_STRING_SESSION") 
    PROXY_SOURCE_IDS_STR = os.environ.get("PROXY_SOURCE_IDS")
    PROXY_TARGET_ID = int(os.environ.get("PROXY_TARGET_ID")) 
    
    # Source IDs ko list of integers mein convert kiya
    source_group_ids = [int(i.strip()) for i in PROXY_SOURCE_IDS_STR.split(',') if i.strip()]
    
except Exception as e:
    print(f"FATAL ERROR: Environment variable setting mein gadbad hai, bro! {e}")
    print("Check karo: PROXY_STRING_SESSION, PROXY_SOURCE_IDS, PROXY_TARGET_ID.")
    exit(1)

# Sanity check
if not all([SESSION_STRING, source_group_ids, PROXY_TARGET_ID]):
    print("FATAL ERROR: Zaroori Environment Variables (SESSION/IDs) set nahi hain.")
    exit(1) 


# === PROXY EXTRACTION LOGIC (All Types) ===

def extract_proxy(text):
    # Pattern 1: Simple IP:PORT
    pattern1 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b' 
    # Pattern 2: IP:PORT:USER:PASS
    pattern2 = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}:\S+:\S+\b'
    # Pattern 3: USER:PASS@IP:PORT 
    pattern3 = r'\b\S+:\S+@\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b'
    # Pattern 4: SOCKS5/SOCKS4 proxy (e.g., socks5: 1.1.1.1:8080)
    pattern4 = r'(socks4|socks5):\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{2,5})'
    # Pattern 5: IP|PORT|USER|PASS (Pipe separated format)
    pattern5 = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\|(\d{2,5})\|(\S+)\|(\S+)'
    # Pattern 6: Hostname:PORT:USER:PASS (Added for webshare type proxies)
    pattern6 = r'\b[a-zA-Z0-9\-\.]+\:\d{2,5}\:\S+\:\S+\b'
    
    # Priority order: Complex (auth/structured) first
    for pattern in [pattern3, pattern2, pattern5, pattern6, pattern4, pattern1]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Formatting the output
            if pattern in [pattern5]:
                return f"SCRAPED PROXY: {match.group(1)}:{match.group(2)}:{match.group(3)}:{match.group(4)}"
            elif pattern == pattern4:
                return f"SCRAPED PROXY ({match.group(1).upper()}): {match.group(2)}:{match.group(3)}"
            else:
                return f"SCRAPED PROXY: {match.group(0)}"
            
    return None


# === TELETHON CLIENT AND COMMAND HANDLER ===

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


@client.on(events.NewMessage(chats=source_group_ids))
async def handler(event):
    msg = event.raw_text
    formatted_proxy = None
    
    # 1. Command Check: Sirf /addproxy ya /proxy se shuru hone wale messages dekhega
    if msg.lower().startswith(('/addproxy', '/proxy')):
        
        # Command ko hata kar proxy string ko extract kiya
        parts = msg.split(maxsplit=1)
        
        # Agar command ke baad koi text (proxy string) hai:
        if len(parts) > 1:
            proxy_string = parts[1].strip() 
            
            # 2. Extract proxy from the isolated string
            formatted_proxy = extract_proxy(proxy_string) 
        
    # 3. Forward the scraped proxy
    if formatted_proxy:
        await client.send_message(PROXY_TARGET_ID, formatted_proxy)
        print(f"Forwarded Command-Scraped Proxy: {formatted_proxy}")


# === START THE CLIENT ===
with client:
    print("Proxy Scraper Bot is running and targeting /addproxy commands...")
    client.run_until_disconnected()