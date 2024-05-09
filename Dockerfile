FROM python:3.10

WORKDIR /app

SHELL ["/bin/bash", "-c"] 

ENV PYHTONUNBUFFERED=1
RUN apt-get update \
  && apt-get -y install tesseract-ocr \
  && apt-get -y install ffmpeg libsm6 libxext6 \
  && apt-get -y install tesseract-ocr-est \
  && apt-get -y install swig \
  && apt-get -y install git

RUN git clone -n --depth=1 --filter=tree:0 https://github.com/estnltk/estnltk.git &&\
      cd estnltk &&\
      git sparse-checkout set —no-cone estnltk &&\
      git checkout &&\
      cd estnltk &&\
      pip install . &&\
      pip install .   

RUN wget -O lemmas.cbow.s100.w2v.bin.gz https://entu.keeleressursid.ee/api2/file-23851?key=I7G5aC1YgdInohMJjUhi1d5e4jLdhQerZ4ikezz1JEv3B9yuJt9KiPl9lrS87Yz0 &&\
    gzip -d lemmas.cbow.s100.w2v.bin.gz


COPY . .

WORKDIR /app/crossword_solver

RUN pip install --upgrade pip &&\
    pip install .

RUN mv /app/lemmas.cbow.s100.w2v.bin /app/crossword_solver/data/lemmas.cbow.s100.w2v.bin

WORKDIR /app/crossword_solver/web
CMD ["python",  "app.py"] 