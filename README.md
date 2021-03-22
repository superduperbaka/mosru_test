# mosru_test
Install

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

Tests
```
pytest 
```

Development
 - set environment according schemas.py file
 - run backend ```docker-compose up backend``` or ```uvicorn backend:app --reload```
 - run rabbit ```docker-compose up rabbit``` or via local service

Run in container

- ```docker-compose build```
- ```docker-compose up```
- ``docker-compose scale producer=x consumer=y`` if need scale

