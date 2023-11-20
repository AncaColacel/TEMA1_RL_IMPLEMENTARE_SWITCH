1 2
## TEMA 1 RL - IMPLEMENTARE SWITCH

## DETALII DE IMPLEMENTARE
Limbaj utilizat pentru implementare -> python.

## DETALII TEHNICE
Voi explica pe scurt cele 2 cerinte pe care le-am rezolvat.
## EX 1. Procesul de comutare.
Am utilizat ca si suport pseudocodul prezentat in cerinta temei. Imi creez un Mac_Table care este stocat intr-un dictionar pentru a retine corespondenta intre adresa MAC si port. Incep prin a introduce in tabela adresa mac sursa a pachetului primit si portul asociat. Verific daca adresa destinatie este unicast sau nu. Pentru asta mi-am creat o metoda prin care sa verific daca adresa este de forma ff:ff:ff:ff:ff:ff, adica adresa de broadcast si daca nu era asa => adresa unicast. Daca era adresa unicast verificam daca se gaseste in tabela adresa destinatie si daca da, trimiteam acolo. In caz contrar trimiteam spre toate celelalte porturi exceptand cel de pe care a venit. Procedam la fel si daca nu era adresa unicast, trimiteam pe toate porturile exceptandu-l pe cel pe care a venit.

## EX 2. VLAN.
Am implementat acest exercitiu peste ceea ce implementasem la primul, deci pe primul l-am modificat pentru a putea oferi suport pentru VLAN. In primul rand, mi-am creat o functie prin care sa parsez fisierele de configurare pe care am apelat-o pe path-urile switchurilor 0 & 1, dupa care am parcurs dictionarul rezultat in care stocasem interfata (cu asocierea sa numerica) si VLAN-ul de care apartine pachetul/T, asta pentru a identifica interfata pe care intra pachetul. Exista 2 cazuri , fiecare cu 2 posibilitati.

**1) Daca primesc de pe access, deci nu am TAG 802.1 q. Daca trimit pe interfata cu Trunk, atasez tag headerului (folosind functia din schelet). Daca trimit pe port cu Vlan am grija sa nu trimit pe portul de pe care a intrat pachetul si sa trimit pe acelasi VLAN.**

**2) Daca primesc de pe Trunk, trimit pe Trunk si pastrez headerul la fel, sau trimit pe Vlan corespunzator cu cel din tag-ul headerului, caz in care folosesc o functie in care elimin tagul, dar returnez noul header fara tag si o structura cu campurile tag-ului ca sa ma pot folosi de ele ulterior. 
Am implementat aceste situatii atat pentru cazul cand adresa era unicast si puteam cunoaste destinatia sau nu o cunoasteam si luam toate interfetele, cat si pentru cazul in care nu era adresa unicast.**

## BIBLIOGRAFIE
- laboratoare && curs
- https://www.cloudflare.com/learning/network-layer/what-is-a-network-switch/


