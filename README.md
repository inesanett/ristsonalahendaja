# Ristsõnalahendaja

Tegu on eestikeelsete ristsõnade lahendajaga, mis võtab ette pildi ristsõnast ning kuvab võimalikud lahendused. Programm eeldab, et ristsõna koosneb ristkülikukujulistest lahtritest, mis on sama suured. Pildil ei tohi ruudustik olla moonutatud, programm eeldab, et ruudustiku jooned lõikuvad täisnurga all.

## Projekti käivitamine

1) Salvesta projekt arvutisse

2) Lae alla Docker Desktop

3) Jooksuta ristsõnalahendaja kaustas (seal kus asub Dockerfile) käsureal järgnevaid käske:
 
      *docker build -t ristsona .* 
    
      *docker run -p 5000:5000 ristsona* 

4) Mine lehele [127.0.0.1:5000](http://127.0.0.1:5000) ja järgi veebilehel kirjeldatud juhiseid
