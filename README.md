# Engeto-project3
3rd project for Python Academy by Engeto

#--------------------------------------------------------------------------------------------------------------------------------------------
Vytvoření virtuálního prostředí:
PS C:\Users\Innovative IT\Documents\Engeto\Projekt1\projekt_3> python -m venv virtualenv

Zpřístupnění skriptů:
PS C:\Users\Innovative IT\Documents\Engeto\Projekt1\projekt_3> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy AllSigned

Aktivace virtuálního prostředí: 
PS C:\Users\Innovative IT\Documents\Engeto\Projekt1\projekt_3> virtualenv\Scripts\activate

Instalace knihoven třetích stran:
PS C:\Users\Innovative IT\Documents\Engeto\Projekt1\projekt_3> pip install JménoKnihovny (pip install requests, pip install beautifulsoup4)

Zjištění požadavků:
PS C:\Users\Innovative IT\Documents\Engeto\Projekt1\projekt_3> pip freeze > Requirements.txt

Načtení požadavků: 
PS C:\Users\Innovative IT\Documents\Engeto\Projekt1\projekt_3> pip install -r Requirements.txt

#--------------------------------------------------------------------------------------------------------------------------------------------

Spuštění programu:
python election_scraper.py "zadane_mesto" "nazev_souboru"

#--------------------------------------------------------------------------------------------------------------------------------------------

Popis programu election_scraper.py:

funkce main():
    0) Ověří, zda byl zadán správný počet argumentů (2) 
    1) Vykoná funkci election_scraper(zadane_mesto, nazev_souboru)
funkce election_scraper(zadane_mesto, nazev_souboru):
    0) Zjistí města na územní úrovni (https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ)
       - pozn: tento krok je oproti zadání navíc - přes název města se dostane na url, kterou jsme dle zadání projektu mohli rovnou zadat - jelikož 
               zadávání názvu města je uživatelsky přívětivější než práce s url 
    1) Prověří, zda se zadane_mesto nachází v seznamu a zda zadaný nazev_souboru má koncovku .csv; pokud ano, pokračuje dál
    2) Pokračuje od města na územní úrovni skrz link X na obecní úroveň, uloží kód a název pro každé město na obecní úrovni
    3) Pokračuje od města na obecní úrovni skrz link X a rozhodne dle nadpisu první tabulky, zda link vede na seznam okrsků, nebo na výsledky daného   města
       - v případě měst jednoduše vyscrapuje hodnoty výsledků (registred, envelopes, valid, volebni strana, počet hlasů)
       - v případě okrsků sečte hodnoty vyscrapovaných výsledků všech okrsků daného města a součet přiřadí danému městu
    4) Vypíše získané výsledky do souboru s názvem nazev_souboru

#--------------------------------------------------------------------------------------------------------------------------------------------

Ukázka průběhu programu election_scraper.py:

1) město s okrsky (výsledky v souboru vysledky_Praha.csv):
![image](https://github.com/Manakili/Engeto-project3/assets/128411481/2b6e3c0b-48c9-428a-a5f2-bd50e50b7d56)

2) město bez okrsků (výsledky v souboru vysledky_Prostějov.csv):
![image](https://github.com/Manakili/Engeto-project3/assets/128411481/17503e41-1f52-4130-afb2-1299feb41a40)
