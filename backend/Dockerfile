FROM python:3.9

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./ /app

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]

ENTRYPOINT ["bash", "./entrypoint.sh"]