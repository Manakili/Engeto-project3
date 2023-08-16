"""
election_scraper.py: třetí projekt do Engeto Online Python Akademie
author: Zuzana Soudná
email: zuza.soudna@gmail.com
discord: Zuzana S.#3996
"""



import requests 
from bs4 import BeautifulSoup, Tag
import csv
import traceback
import sys


#----------------------------------------------------------------------------
#Funkce election_scraper:
#1) Prověří: zadané město se nachází v seznamu na webu, požadovaný soubor má koncovku .csv
#2) Na webu najde všechny tabulky s okresními městy, najde k nim příslušející linky 
#3) Rozhodne, zda je link na web s okresy, nebo městy
#   - v případě měst jednoduše vyscrapuje hodnoty
#   - v případě okresů sečte hodnoty vyscrapované pro města v každém okresu
#4)  
def election_scraper(zadane_mesto: str, nazev_souboru: str):
    
    #tabulky s městy na územní úrovni
    url_uzemni_uroven = "https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"
    odp_serveru = requests.get(url_uzemni_uroven)
    soup = BeautifulSoup(odp_serveru.text, "html.parser")
    vsechny_tabulky_uzemni_uroven = soup.find_all("table", {"class": "table"})

    #identifikace všech měst na územní úrovni
    slovnik_uzemni_uroven = dict()
    for tabulka in vsechny_tabulky_uzemni_uroven:
        vsechna_tr_uzemni_uroven = tabulka.find_all("tr")
        vsechna_mesta_uzemni_uroven = vsechna_tr_uzemni_uroven[2:]

        #identifikace linků příslušejících daným městům územní úrovně
        #a vytvoření slovníku územní urovně
        for tr in vsechna_mesta_uzemni_uroven:
            td_radky_uzemni_uroven = tr.find_all("td")
            mesto_uzemni_uroven = td_radky_uzemni_uroven[1].getText()
            mesto_uzemni_uroven_url = td_radky_uzemni_uroven[3].a.attrs
            slovnik_uzemni_uroven[mesto_uzemni_uroven] = mesto_uzemni_uroven_url["href"]
               
    #ověření, že zadané město je v seznamu měst územní úrovně a zadaný soubor má správný formát .csv
    if zadane_mesto in slovnik_uzemni_uroven and ".csv" in nazev_souboru:
        print("Město je v seznamu, název souboru je zadán správně.")

        #tabulky s městy na úrovni obcí
        url_obecni_uroven = f"https://volby.cz/pls/ps2017nss/{slovnik_uzemni_uroven[zadane_mesto]}"
        odp_serveru_obecni_uroven = requests.get(url_obecni_uroven)
        soup_obecni_uroven = BeautifulSoup(odp_serveru_obecni_uroven.text, "html.parser")
        vsechny_tabulky_obecni_uroven = soup_obecni_uroven.find_all("table", {"class": "table"})

        #vytvoření slovníku pro obecní úroveň
        slovnik_obecni_uroven = dict()
        slovnik_obecni_uroven = {url_obecni_uroven : []}

        #tabulky s městy na obecní úrovni
        for tabulka in vsechny_tabulky_obecni_uroven:
            vsechna_tr_obecni_uroven = tabulka.find_all("tr")
            vsechna_mesta_obecni_uroven = vsechna_tr_obecni_uroven[2:]
        
            #identifikace všech kodů a měst na obecní úrovni
            for tr in vsechna_mesta_obecni_uroven:
                td_radky_obecni_uroven = tr.find_all("td")
                kod_mesta_obecni_uroven = td_radky_obecni_uroven[0].getText()
                mesto_obecni_uroven = td_radky_obecni_uroven[1].getText()
                url_predvolba = "https://volby.cz/pls/ps2017nss/"
                
                #identifikace linků pro města na obecní úrovni
                if type(td_radky_obecni_uroven[2].a) == Tag:
                    mesto_url_obecni_uroven = td_radky_obecni_uroven[2].a.attrs
                    mesto_url_obecni_uroven_string = str(mesto_url_obecni_uroven["href"])
                    mesto_url_obecni_uroven_cele = url_predvolba + mesto_url_obecni_uroven_string
                    
                    prvky_slovnik_obecni_uroven = kod_mesta_obecni_uroven, mesto_obecni_uroven, mesto_url_obecni_uroven_cele
                    slovnik_obecni_uroven.setdefault(url_obecni_uroven,[]).append(prvky_slovnik_obecni_uroven)
                else: 
                    break

        print(f"Stahuji data pro {zadane_mesto} z {url_obecni_uroven}.")

        #průchod url po obecní úrovni = seznam okrsků, nebo výsledky pro město na obecní úrovni
        z=0
        soucty_registred = {}
        soucty_envelopes = {}
        soucty_valid = {}
        slovnik_volebni_strany = dict()
        while z < len(slovnik_obecni_uroven[url_obecni_uroven]):  
            soucty_registred[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = 0
            soucty_envelopes[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = 0
            soucty_valid[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = 0
            slovnik_volebni_strany[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = {}
            
            odp_serveru_okrsek_nebo_obec = requests.get(slovnik_obecni_uroven[url_obecni_uroven][z][2])
            soup_okrsek_nebo_obec = BeautifulSoup(odp_serveru_okrsek_nebo_obec.text, "html.parser")
            vsechny_tabulky_okrsek_nebo_obec = soup_okrsek_nebo_obec.find_all("table", {"class": "table"})    

            #identifikace, zda se jedná o okrsky, nebo výsledky měst na úrovni obcí, podle nadpisu první tabulky
            for index, tabulka in enumerate(vsechny_tabulky_okrsek_nebo_obec):
                if index == 0:        
                    tr_tabulka_1 = tabulka.find_all("tr")
                    nadpis_tabulka_1 = tr_tabulka_1[0].find("th").getText()
                    
                    #1) cyklus pro výsledky měst na úrovni obcí
                    if nadpis_tabulka_1 == "Okrsky": 
                            
                        i=0
                        while i < len(slovnik_obecni_uroven[url_obecni_uroven]):
                            for index, tabulka in enumerate(vsechny_tabulky_okrsek_nebo_obec,0):
                                
                                #scraping výsledků z první tabulky (registred, envelopes, valid)
                                if index == 0:
                                    okrsek_mesta = tabulka.find_all("tr")
                                    vsechna_td = okrsek_mesta[2].find_all("td")
                
                                    registred = vsechna_td[3].getText()
                                    envelopes = vsechna_td[4].getText()
                                    valid = vsechna_td[7].getText()

                                    registred_int = int(registred.replace(u'\xa0', u''))
                                    envelopes_int = int(envelopes.replace(u'\xa0', u''))
                                    valid_int = int(valid.replace(u'\xa0', u''))
                                    
                                    soucty_registred[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = registred_int
                                    soucty_envelopes[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = envelopes_int
                                    soucty_valid[slovnik_obecni_uroven[url_obecni_uroven][z][1]] = valid_int
                                
                                #scraping výsledků z dalších tabulek (volební strany, počet hlasů)
                                else:
                                    k = 2
                                    volebni_strany = tabulka.find_all("tr")
                                    k_hotovo = False
                                    while k < (len(volebni_strany)-1):
                                        vsechna_td = volebni_strany[k].find_all("td")
                                        volebni_strana = vsechna_td[1].getText()
                                        pocet_hlasu = vsechna_td[2].getText()
                                        slovnik_volebni_strany[slovnik_obecni_uroven[url_obecni_uroven][z][1]].update( {volebni_strana: pocet_hlasu})
                                        
                                        k += 1     
                                    k_hotovo = True
                            i += 1
                            if k_hotovo == True:
                                break        
                            
                        if k_hotovo == True:
                                break

                    #2) cyklus pro seznam okrsků (výsledky pro jednotlivé okrsky se budou sčítat)  
                    if nadpis_tabulka_1 == "Okrsek": 
                        
                        sum_registred = 0
                        sum_envelopes = 0
                        sum_valid = 0

   
                        for tr in tr_tabulka_1:
                            vsechna_td_okresku = tr.find_all("td", {"class": "cislo"} )
                    
                            for td in vsechna_td_okresku:
                                vsechna_a_okresku = td.a.attrs
                                url_okrsky_string = vsechna_a_okresku["href"]
                                url_okrsky_cele = url_predvolba + url_okrsky_string
                                
                                odp_serveru_okrsky = requests.get(url_okrsky_cele)
                                soup_okrsky = BeautifulSoup(odp_serveru_okrsky.text, "html.parser")
                                vsechny_tabulky_4 = soup_okrsky.find_all("table", {"class": "table"}) 


                                i=0
                                while i < 1:
                                        sum_registred = 0
                                        sum_envelopes = 0
                                        sum_valid = 0
                                        for index, tabulka in enumerate(vsechny_tabulky_4,0):
                                            
                                            #scraping výsledků z první tabulky (registred, envelopes, valid)
                                            if index == 0:
                                                okrsek_mesta = tabulka.find_all("tr")
                                                vsechna_td = okrsek_mesta[1].find_all("td")
                                            
                                                registred = vsechna_td[0].getText()
                                                envelopes = vsechna_td[1].getText()
                                                valid = vsechna_td[4].getText()
                                                registred_int = int(registred.replace(u'\xa0', u''))
                                                envelopes_int = int(envelopes.replace(u'\xa0', u''))
                                                valid_int = int(valid.replace(u'\xa0', u''))

                                                #součty hodnot z první tabulky
                                                sum_registred = sum_registred + registred_int
                                                soucty_registred[slovnik_obecni_uroven[url_obecni_uroven][z][1]] += registred_int
                                                
                                                sum_envelopes = sum_registred + envelopes_int
                                                soucty_envelopes[slovnik_obecni_uroven[url_obecni_uroven][z][1]] += envelopes_int
                                        
                                                sum_valid = sum_valid + valid_int
                                                soucty_valid[slovnik_obecni_uroven[url_obecni_uroven][z][1]] += valid_int
                                            
                                            #scraping výsledků z dalších tabulek (volební strany, počet hlasů)    
                                            else:
                                                k = 2
                                                volebni_strany = tabulka.find_all("tr")
                                                k_hotovo = False
                                                while k < (len(volebni_strany)-1):
                                                    vsechna_td = volebni_strany[k].find_all("td")
                                                    volebni_strana = vsechna_td[1].getText()
                                                    pocet_hlasu = vsechna_td[2].getText()
                                                    pocet_hlasu_int = int(pocet_hlasu.replace(u'\xa0', u''))
                                                    
                                                    #součty hlasů z dalších tabulek
                                                    if slovnik_volebni_strany[slovnik_obecni_uroven[url_obecni_uroven][z][1]].get(volebni_strana) is None:
                                                        slovnik_volebni_strany[slovnik_obecni_uroven[url_obecni_uroven][z][1]][volebni_strana] = pocet_hlasu_int
                                                    else:
                                                        slovnik_volebni_strany[slovnik_obecni_uroven[url_obecni_uroven][z][1]].update(
                                                            {volebni_strana:slovnik_volebni_strany[slovnik_obecni_uroven[url_obecni_uroven][z][1]][volebni_strana] 
                                                            + pocet_hlasu_int})
                                                    k += 1   
                                                k_hotovo = True
                                        i += 1
                                        
                    else: 
                        print("Tabulka nepatří ani mezi obce, ani mezi okrsky.")
                        continue
                else: 
                    print("Na stránce není žádná tabulka.") 
                    continue
            z += 1

        #Slovníky hodnot vyscrapovaných v předchozím kroku pro každé město zvlášť
        #se v cyklu přepíšou do listu všech jednotlivých slovníků, kde 
        #klíče mají názvy kategorií
        vysledky = dict()
        list_vysledku = list()
        s = 0
        while s < len(slovnik_obecni_uroven[url_obecni_uroven]): 
            sada_klic_hodnota = {"code" : slovnik_obecni_uroven[url_obecni_uroven][s][0], "location" : slovnik_obecni_uroven[url_obecni_uroven][s][1]}
            vysledky.update(sada_klic_hodnota)
            soucty_registred_klic_hodnota = {"registered" : soucty_registred[slovnik_obecni_uroven[url_obecni_uroven][s][1]]}
            vysledky.update(soucty_registred_klic_hodnota)
            
            soucty_envelopes_klic_hodnota = {"envelopes" : soucty_envelopes[slovnik_obecni_uroven[url_obecni_uroven][s][1]]}
            vysledky.update(soucty_envelopes_klic_hodnota)
            
            soucty_valid_klic_hodnota = {"valid" : soucty_valid[slovnik_obecni_uroven[url_obecni_uroven][s][1]]}
            vysledky.update(soucty_valid_klic_hodnota)
          
            hodnoty_voleb = list(slovnik_volebni_strany)[s]
            
            vysledky.update(slovnik_volebni_strany.get(hodnoty_voleb))

            vysledky_kopie = vysledky.copy()
            list_vysledku.append(vysledky_kopie)

            s += 1
         
        #print(list_vysledku) #Pro závěrečnou kontrolu výpisu vyscapovaných hodnot

        #Zápis výsledného listu slovníků s vyscrapovanými údaji do souboru
        try:
            csv_soubor = open(nazev_souboru, mode="w", encoding="CP1250", newline= "" )
            sloupce = list_vysledku[0].keys()
            headerList = list_vysledku[0].keys()
         
        except FileExistsError:
            return traceback.format_exc()
        except IndexError:
            return traceback.format_exc()
        else:
            print(f"Ukládám data do souboru {nazev_souboru}.")
            zapis = csv.DictWriter(csv_soubor, fieldnames=sloupce, delimiter= ";")
            zapis.writeheader()
            zapis.writerows(list_vysledku)
            return "Saved"
        finally:
            csv_soubor.close()


    elif zadane_mesto in slovnik_uzemni_uroven and ".csv" not in nazev_souboru:    
        print("Město je v seznamu, ale název souboru je zadán nesprávně.")
    elif zadane_mesto not in slovnik_uzemni_uroven and ".csv" in nazev_souboru:    
        print("Město není v seznamu, název souboru je zadán správně.")   
    elif zadane_mesto not in slovnik_uzemni_uroven and ".csv" not in nazev_souboru:
        print("Město není v seznamu, ani název souboru není zadán správně.")
    
#----------------------------------------------------------------------------

def main():
    #"""
    #Funkce proveri spravnost poctu zadanych argumentu, 
    #v pripade spravneho poctu scrapuje udaje z webove stranky.
    #"""

    if len(sys.argv) == 1: 
        print(
            "Pro spuštění chybí oba potřebné argumenty.",
            "Zapiš: python election_scraper.py 'zadane_mesto' 'nazev_souboru'", sep="\n"
        )
    elif len(sys.argv) == 2: 
        print(
            "Pro spuštění chybí jeden z potřebných argumentů.",
            "Zapiš: python election_scraper.py 'zadane_mesto' 'nazev_souboru'", sep="\n"
        )
    elif len(sys.argv) == 3:
        election_scraper(sys.argv[1], sys.argv[2])
        print(f"Ukončuji election_scraper.")

#----------------------------------------------------------------------------

main()

