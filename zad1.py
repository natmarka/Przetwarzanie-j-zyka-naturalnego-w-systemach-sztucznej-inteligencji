import gzip
import os
import matplotlib.pyplot as plt
import numpy as np

# --- USTAWIENIA ---
nazwa_pliku_gz = 'lemma-WITHOUTnumberssymbols-frequencies-paisa.txt.gz'
# Weźmiemy więcej punktów, żeby wykres był wyraźny, np. 10 000
ile_wyrazow_do_wykresu = 10000
nazwa_pliku_wykresu = 'wykres_zipfa.png'
# --------------------

def stworz_wykres_zipfa(nazwa_pliku, limit):
    """
    Wczytuje dane frekwencyjne, tworzy wykres log-log Prawa Zipfa
    i zapisuje go do pliku.
    """
    if not os.path.exists(nazwa_pliku):
        print(f"\nBŁĄD: Nie znaleziono pliku '{nazwa_pliku}'!")
        return

    print(f"Analizuję plik '{nazwa_pliku}' w celu stworzenia wykresu...")

    # Listy do przechowywania danych dla wykresu
    rangi = []
    czestosci = []

    try:
        with gzip.open(nazwa_pliku, 'rt', encoding='utf-8') as f:
            aktualna_ranga = 1
            for linia in f:
                if aktualna_ranga > limit:
                    break

                linia = linia.strip()
                if not linia or linia.startswith('#'):
                    continue

                czesci = linia.split(',')
                if len(czesci) == 2:
                    try:
                        czestosc = int(czesci[1])
                        
                        # Dodajemy dane do list
                        rangi.append(aktualna_ranga)
                        czestosci.append(czestosc)
                        
                        aktualna_ranga += 1
                    except ValueError:
                        continue
        
        if not rangi:
            print("Nie udało się wczytać żadnych poprawnych danych do stworzenia wykresu.")
            return

        # Obliczanie logarytmów z danych
        log_rangi = np.log(rangi)
        log_czestosci = np.log(czestosci)

        # Tworzenie wykresu
        plt.figure(figsize=(10, 6))
        plt.scatter(log_rangi, log_czestosci, s=5, color='blue', alpha=0.7)
        
        # Dodawanie tytułu i etykiet
        plt.title('Weryfikacja Prawa Zipfa dla języka włoskiego', fontsize=16)
        plt.xlabel('Logarytm z Rangi [log(R)]', fontsize=12)
        plt.ylabel('Logarytm z Częstości [log(f)]', fontsize=12)
        plt.grid(True, which="both", ls="--", linewidth=0.5)

        # Zapisywanie wykresu do pliku
        plt.savefig(nazwa_pliku_wykresu)
        print(f"\nSukces! Wykres został zapisany w pliku: '{nazwa_pliku_wykresu}'")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")


stworz_wykres_zipfa(nazwa_pliku_gz, ile_wyrazow_do_wykresu)