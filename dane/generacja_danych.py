import pandas as pd
from datetime import datetime, timedelta
import random

def random_date(start_date, end_date):
    return start_date + timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds())))

start_date = datetime(2015, 1, 1)
end_date = datetime(2023, 12, 31)

produkty_ceny = {
    "Elektronika": {
        "Laptop": 2500.0,
        "Telefon": 800.0,
        "Kamera": 1200.0
    },
    "Spożywcze": {
        "Chleb": 2.0,
        "Mleko": 3.0,
        "Jogurt": 2.5
    },
    "Odzież": {
        "Koszulka": 15.0,
        "Spodnie": 30.0,
        "Kurtka": 50.0
    }
}

data_transakcji = []
kategorie_list = []
produkty_list = []
liczba = []
cena = []
wartosc = []

for year in range(2015, 2024):
    for month in range(1, 13):
        for _ in range(10):
            data_transakcji.append(random_date(datetime(year, month, 1), datetime(year, month, 28)))
            wybrana_kategoria = random.choice(list(produkty_ceny.keys()))
            kategorie_list.append(wybrana_kategoria)
            wybrany_produkt = random.choice(list(produkty_ceny[wybrana_kategoria].keys()))
            produkty_list.append(wybrany_produkt)
            liczba.append(random.randint(1, 5))
            cena.append(produkty_ceny[wybrana_kategoria][wybrany_produkt])
            wartosc.append(round(liczba[-1] * cena[-1], 2))

df = pd.DataFrame({
    'Data transakcji': data_transakcji,
    'Kategoria': kategorie_list,
    'Produkt': produkty_list,
    'Liczba': liczba,
    'Cena': cena,
    'Wartość': wartosc
})

print(df)
df.to_csv('historiatransakcji.csv', index=False)