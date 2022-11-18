  FROM python:3.9
  LABEL maintainer="Ashik meeran mohideen, ashikmeeranmohideen@gmail.com"
  RUN apt-get update
  RUN mkdir /app
  WORKDIR /app
  COPY . /app
  RUN pip install -r requirements.txt
  EXPOSE 5000
  ENTRYPOINT [ "flask"]
  CMD [ "run", "--host", "0.0.0.0" ]