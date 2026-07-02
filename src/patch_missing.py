import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

CLUBS = {
    "Real Madrid": 418, "FC Barcelona": 131, "Atlético Madrid": 13, "Valencia CF": 1049,
    "Sevilla FC": 368, "Villarreal CF": 1050, "Athletic Bilbao": 621, "Celta Vigo": 940,
    "Real Sociedad": 681, "Real Betis": 150, "Getafe CF": 3709, "RCD Espanyol": 714,
    "Deportivo Alavés": 1108
}

def clean_currency(value_str):
    if not value_str or value_str.strip() in ['-', '€0', '']: return 0.0
    val = value_str.replace('€', '').strip()
    multiplier = 1.0
    if 'm' in val or 'M' in val:
        multiplier = 1.0; val = val.replace('m', '').replace('M', '')
    elif 'k' in val or 'K' in val:
        multiplier = 0.001; val = val.replace('k', '').replace('K', '')
    elif 'bn' in val or 'B' in val:
        multiplier = 1000.0; val = val.replace('bn', '').replace('B', '')
    try: return round(float(val) * multiplier, 2)
    except ValueError: return 0.0

df = pd.read_csv('data/raw/tm_data.csv', sep=';')
patched = 0

for idx, row in df.iterrows():
    club = row['Club']
    season_str = row['Season']
    season_year = int(season_str.split('/')[0])
    club_id = CLUBS[club]
    
    if row['Squad_Value_TM'] == 0.0:
        print(f"Patching MV for {club} {season_year}...")
        url_mv = f"https://www.transfermarkt.com/club/kader/verein/{club_id}/saison_id/{season_year}"
        try:
            res = requests.get(url_mv, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            total = 0.0
            mvs = soup.find_all('td', class_='rechts hauptlink')
            for mv in mvs: total += clean_currency(mv.text)
            if total > 0:
                df.at[idx, 'Squad_Value_TM'] = round(total, 2)
                patched += 1
        except Exception as e: print(f"Failed {club} {season_year}: {e}")
        time.sleep(1.5)
        
    if row['Transfer_Expenditures'] == 0.0 and row['Transfer_Revenues'] == 0.0:
        # Check if it was a timeout or genuinely 0
        url_tr = f"https://www.transfermarkt.com/club/transfers/verein/{club_id}/saison_id/{season_year}"
        try:
            res = requests.get(url_tr, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            inc_elem = soup.find(string=lambda text: text and 'Income' in text)
            if inc_elem and inc_elem.parent and inc_elem.parent.parent:
                match = re.search(r'€([0-9\.]+)[mkb]?', inc_elem.parent.parent.text.strip(), re.IGNORECASE)
                if match: df.at[idx, 'Transfer_Revenues'] = clean_currency('€' + match.group(0).replace('€',''))
                    
            exp_elem = soup.find(string=lambda text: text and 'Expenditure' in text)
            if exp_elem and exp_elem.parent and exp_elem.parent.parent:
                match = re.search(r'€([0-9\.]+)[mkb]?', exp_elem.parent.parent.text.strip(), re.IGNORECASE)
                if match: df.at[idx, 'Transfer_Expenditures'] = clean_currency('€' + match.group(0).replace('€',''))
        except Exception as e: print(f"Failed Transfer {club} {season_year}: {e}")
        time.sleep(1.5)

df.to_csv('data/raw/tm_data.csv', index=False, sep=';')
print(f"Done. Patched {patched} missing values.")
