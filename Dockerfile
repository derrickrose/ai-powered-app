FROM python:3.11-slim

WORKDIR /app

# torch en version CPU : image ~2 Go plus légère que la version CUDA par défaut
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# requirements.txt doit être copié AVANT le pip install (sinon le build échoue)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && python -m spacy download en_core_web_md \
 && python -m nltk.downloader -d /usr/local/share/nltk_data stopwords

COPY . /app

CMD ["python", "server.py"]
