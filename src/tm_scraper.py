import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

CLUBS = {
    "Real Madrid": 418,
    "FC Barcelona": 131,
    "Atlético Madrid": 13,
    "Valencia CF": 1049,
    "Sevilla FC": 368,
    "Villarreal CF": 1050,
    "Athletic Bilbao": 621,
    "Celta Vigo": 940,
    "Real Sociedad": 681,
    "Real Betis": 150,
    "Getafe CF": 3709,
    "RCD Espanyol": 714,
    "Deportivo Alavés": 1108
}

def clean_currency(value_str):
    if not value_str or value_str.strip() in ['-', '€0', '']:
        return 0.0
    val = value_str.replace('€', '').strip()
    multiplier = 1.0
    if 'm' in val or 'M' in val:
        multiplier = 1.0
        val = val.replace('m', '').replace('M', '')
    elif 'k' in val or 'K' in val:
        multiplier = 0.001
        val = val.replace('k', '').replace('K', '')
    elif 'bn' in val or 'B' in val:
        multiplier = 1000.0
        val = val.replace('bn', '').replace('B', '')
    try:
        return round(float(val) * multiplier, 2)
    except ValueError:
        return 0.0

def scrape_all():
    data = []
    
    for club_name, club_id in CLUBS.items():
        for season_year in range(2015, 2025): # 2015 to 2024
            season_str = f"{season_year}/{str(season_year+1)[-2:]}"
            print(f"Scraping {club_name} - {season_str}...")
            
            row = {
                "Club": club_name,
                "Season": season_str,
                "Squad_Value_TM": 0.0,
                "Transfer_Expenditures": 0.0,
                "Transfer_Revenues": 0.0
            }
            
            # 1. Market Value (Iterating over players to sum up historical value)
            url_mv = f"https://www.transfermarkt.com/club/kader/verein/{club_id}/saison_id/{season_year}"
            try:
                res_mv = requests.get(url_mv, headers=HEADERS, timeout=10)
                soup_mv = BeautifulSoup(res_mv.text, 'html.parser')
                table = soup_mv.find('table', class_='items')
                total_val = 0.0
                if table:
                    # TM puts market values in td class 'rechts hauptlink'
                    mvs = table.find_all('td', class_='rechts hauptlink')
                    for mv in mvs:
                        total_val += clean_currency(mv.text)
                row["Squad_Value_TM"] = round(total_val, 2)
            except Exception as e:
                print(f"Error fetching MV for {club_name} {season_year}: {e}")
            
            time.sleep(1.0)
            
            # 2. Transfers
            url_tr = f"https://www.transfermarkt.com/club/transfers/verein/{club_id}/saison_id/{season_year}"
            try:
                res_tr = requests.get(url_tr, headers=HEADERS, timeout=10)
                soup_tr = BeautifulSoup(res_tr.text, 'html.parser')
                
                # Income
                inc_elem = soup_tr.find(string=lambda text: text and 'Income' in text)
                if inc_elem and inc_elem.parent and inc_elem.parent.parent:
                    inc_text = inc_elem.parent.parent.text.strip()
                    # Expecting something like: "Income\n12\n\n€24.15m"
                    match = re.search(r'€([0-9\.]+)[mkb]?', inc_text, re.IGNORECASE)
                    if match:
                        row["Transfer_Revenues"] = clean_currency('€' + match.group(0).replace('€',''))
                
                # Expenditure
                exp_elem = soup_tr.find(string=lambda text: text and 'Expenditure' in text)
                if exp_elem and exp_elem.parent and exp_elem.parent.parent:
                    exp_text = exp_elem.parent.parent.text.strip()
                    match = re.search(r'€([0-9\.]+)[mkb]?', exp_text, re.IGNORECASE)
                    if match:
                        row["Transfer_Expenditures"] = clean_currency('€' + match.group(0).replace('€',''))
            except Exception as e:
                print(f"Error fetching transfers for {club_name} {season_year}: {e}")

            data.append(row)
            time.sleep(1.0)
            
    df = pd.DataFrame(data)
    df.to_csv('data/raw/tm_data.csv', index=False, sep=';')
    print("Scraping completed. Saved to data/raw/tm_data.csv")

if __name__ == "__main__":
    scrape_all()
