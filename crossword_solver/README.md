# Ristsõnalahendaja

Tegu on eestikeelsete ristsõnade lahendajaga, mis võtab ette pildi ristsõnast ning kuvab võimalikud lahendused.

## Projekti käivitamine

Projekti juhend käib Windows operatsioonisüsteemi kohta.

1) Salvesta projekt arvutisse.

2) Lae Eesti Keeleressursside Keskuse veebilehelt alla eeltreenitud Word2Vec mudel "lemmas.cbow.s100.w2v.bin.gz", mille leiad siit: https://entu.keeleressursid.ee/shared/7540/I7G5aC1YgdInohMJjUhi1d5e4jLdhQerZ4ikezz1JEv3B9yuJt9KiPl9lrS87Yz0. Paki fail lahti ning lisa mudel data kausta.

3) Programm toimimiseks on vaja installida Tesseract-OCR. See on Windowsile kättesaadaval aadressil https://github.com/UB-Mannheim/tesseract/wiki (tesseract-ocr-w64-setup-5.3.3.20231005.exe (64 bit)). Faili käivitamisel antakse ette juhised installimiseks. Oluline on sammul "Choose components" jälgida, et installitakse "Additional language data" all eesti keel. Tesseracti kaustale viitav tee tuleb lisada Windowsi keskkonnamuutujate alla. Selleks leiab juhised näiteks siit: https://ironsoftware.com/csharp/ocr/blog/ocr-tools/install-tesseract/.

5) Loo virtuaalkeskkond endale meelepärasel viisil. Näiteks Anaconda kaudu on võimalik luua virtuaalkeskkond jooksutades käsureal käsku "conda create -n ristsona python=3.10". Sisene keskkonda käsuga "conda activate ristsona".

6) Liigu käsureal projekti crossword_solver kausta ning jooksuta käsku "pip install -e ."

7) Veebirakenduse käitamiseks liigu kausta "web" ning jooksuta käsku "python app.py". Liigu tagastatud veebiaadressile ning järgi seal antud juhiseid.



