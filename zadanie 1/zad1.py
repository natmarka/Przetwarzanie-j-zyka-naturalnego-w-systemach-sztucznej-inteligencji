import gzip
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import networkx as nx

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

    # Regresja liniowa log-log
    slope, intercept, r_value, p_value, std_err = linregress(log_rangi, log_czestosci)

    print(f"\nWspółczynnik nachylenia (s): {slope:.3f}")
    print(f"Współczynnik determinacji R²: {r_value**2:.4f}")

    # Dodaj linię regresji do wykresu
    plt.plot(log_rangi, intercept + slope * log_rangi, color='red', linewidth=1.5, label=f'Nachylenie = {slope:.2f}')
    plt.legend()


stworz_wykres_zipfa(nazwa_pliku_gz, ile_wyrazow_do_wykresu)


def znajdz_slowa_90proc(nazwa_pliku):
    slowa = []
    czestosci = []

    with gzip.open(nazwa_pliku, 'rt', encoding='utf-8') as f:
        for linia in f:
            if not linia.strip() or linia.startswith('#'):
                continue
            czesci = linia.split(',')
            if len(czesci) == 2:
                slowo, freq = czesci
                try:
                    czestosc = int(freq)
                    slowa.append(slowo)
                    czestosci.append(czestosc)
                except ValueError:
                    continue

    suma = sum(czestosci)
    prog = 0.9 * suma

    suma_biezaca = 0
    indeks = 0
    while suma_biezaca < prog and indeks < len(czestosci):
        suma_biezaca += czestosci[indeks]
        indeks += 1

    print(f"\nLiczba słów potrzebnych do pokrycia 90% języka: {indeks}")
    print(f"Przykładowe najczęstsze słowa: {slowa[:20]}")

    return slowa[:indeks]

znajdz_slowa_90proc(nazwa_pliku_gz)



def stworz_graf_korelacji(nazwa_pliku, limit=2000):
    """
    Tworzy graf współwystępowania słów na podstawie danych korpusu.
    Pomija linie z metadanymi i linkami.
    """
    G = nx.Graph()
    poprzedni = None  # 🔹 inicjalizacja zmiennej przed pętlą

    with gzip.open(nazwa_pliku, 'rt', encoding='utf-8') as f:
        for i, linia in enumerate(f):
            if i > limit:
                break

            linia = linia.strip()

            # 🔹 Pomijamy komentarze, puste linie, linki i metadane
            if not linia or linia.startswith('#') or 'http' in linia or 'www' in linia:
                continue

            czesci = linia.split(',')
            if len(czesci) != 2:
                continue

            slowo, freq = czesci
            slowo = slowo.strip()

            # 🔹 Pomijamy liczby i pojedyncze znaki
            if not slowo.isalpha() or len(slowo) < 2:
                continue

            # 🔹 Tworzymy połączenie tylko jeśli mamy poprzednie słowo
            if poprzedni is not None:
                G.add_edge(poprzedni, slowo)

            poprzedni = slowo  # zapamiętaj bieżące słowo jako poprzednie dla następnego kroku

    print(f"Graf ma {len(G.nodes())} węzłów i {len(G.edges())} krawędzi.")

    plt.close('all')
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.5, seed=42)
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color='skyblue', alpha=0.8)
    nx.draw_networkx_edges(G, pos, alpha=0.4)
    nx.draw_networkx_labels(G, pos, font_size=8)
    plt.title(f"Graf współwystępowania słów w języku włoskim dla {limit} słów", fontsize=14)
    plt.axis("off")
    plt.savefig("graf_wloski.png", dpi=300, bbox_inches='tight')

stworz_graf_korelacji(nazwa_pliku_gz, limit=200)
