# Ristsõnalahendaja

Tegu on eestikeelsete ristsõnade lahendajaga, mis võtab ette pildi ristsõnast ning kuvab võimalikud lahendused. Programm eeldab, et ristsõna koosneb ristkülikukujulistest lahtritest, mis on sama suured. Pildil ei tohi ruudustik olla moonutatud, programm eeldab, et ruudustiku jooned lõikuvad täisnurga all.

## Ligipääs veebilehe kaudu

Loodud ristsõnalahendaja on ülespandud ülikooli serverisse ning sellele saab ligi järgneva veebilehe kaudu: [https://ristsonalahendaja.cs.ut.ee/](https://ristsonalahendaja.cs.ut.ee/). Antud veebiserver ei suuda hallata korraga palju kasutajaid. Juhul kui lehte kasutab korraga mitu inimest võib rakendus muutuda väga aeglaseks.


## Projekti käivitamine Dockeri kaudu

Soovi korral on võimalik katsetada projekti ka oma arvutis. Selleks läbi järgmised sammud:

1) Salvesta projekt arvutisse

2) Lae alla Docker Desktop ning käivita rakendus

3) Jooksuta ristsõnalahendaja kaustas (seal kus asub Dockerfile) käsureal järgnevaid käske:
 
      *docker build -t ristsona .* 
    
      *docker run -p 5000:5000 ristsona* 

4) Mine lehele [127.0.0.1:5000](http://127.0.0.1:5000) ja järgi veebilehel kirjeldatud juhiseid
