FROM python:3.10.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && pip install --upgrade pip \
    && pip install pipenv

COPY Pipfile* ./

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --skip-lock

RUN pip install -U nltk

RUN python -c "import nltk; nltk.download('punkt')"

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 81

CMD ["pipenv", "run", "streamlit", "run", "app/main.py", "--server.port=81"]