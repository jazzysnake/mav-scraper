FROM python:3.8
 
WORKDIR /scraper
COPY . /scraper
 
RUN pip install -r requirements.txt
 
WORKDIR /scraper/src
ENTRYPOINT ["python"]
CMD ["mav-scraper.py"]
