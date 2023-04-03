# Sistema de Gerenciamento e Controle de Agravos - Backend
<br>
O backend utiliza o Django + Django Rest Framework + MySQL + Bootstrap 4 (via [Django jazzmin](https://github.com/farridav/django-jazzmin)).

# Seguiremos a recomendação de escrita de código no estilo do PEP 008 do Python:
https://www.python.org/dev/peps/pep-0008

<br>

### Requisitos do Sistema:
- git (Controle de Versão e acesso ao repositório)
    - [Debia/Ubuntu] sudo apt install git
    - [Arch/Majaro] sudo pacman -S git
    - [mac] brew install git
- mysql (Banco de dados)
    - [Debia/Ubuntu] sudo apt install libmysqlclient-dev
    - [Arch/Majaro] sudo apt install mysql-server && sudo mysql_secure_installation
    - [mac] brew install mysql && brew services start mysql && mysql_secure_installation
    - [mac] brew install openssl
- python (>= 3.8)
    - [Debia/Ubuntu] sudo apt install libpq-dev python3-dev python3-pip
    - [Arch/Majaro] Distros baseadas no Arch Linux já vem com o python3.
    - [Debia/Ubuntu] sudo apt install build-essential libssl-dev libffi-dev python-dev
- rabbitmq (message queue - necessário para integração com o Celery)
    - [Debia/Ubuntu] - [sudo apt install rabbitmq-server] (https://attacomsian.com/blog/install-rabbitmq-macos-ubuntu)
    - [Arch/Majaro] sudo pacman -S rabbitmq
    - [mac] brew install rabbitmq && export PATH=$PATH:/usr/local/sbin && rabbitmq-server start or brew services start rabbitmq
- python-rsa (Criptografia de dados)
    - [Debia/Ubuntu] sudo apt install python-rsa
    - [Arch/Majaro] sudo pacman -S python-rsa
- development tools
    - [Visual Studio Code](https://code.visualstudio.com/download)
    - [MySQL Workbench](https://dev.mysql.com/downloads/workbench)
    - [phpMyAdmin](https://www.phpmyadmin.net)

<br>

### Criar o banco de dados
```
sudo mysql -u root -p
mysql> CREATE DATABASE <db_name> CHARACTER SET utf8;
mysql> CREATE USER '<db_name>'@'%' IDENTIFIED WITH mysql_native_password BY '<password-here>';
mysql> GRANT ALL ON <db_name>.* TO '<db_name>'@'%';
mysql> FLUSH PRIVILEGES;
```

### Criar o arquivo .env com as informações do banco e demais variáveis
1. Copiar o arquivo de exemplo na mesma pasta e renomear para ".env".<br>O arquivo de exemplo está em: application/.env.example
2. Gerar o SECRET_KEY para o .env
```
python3 -c 'import secrets; print(secrets.token_hex(30))'
```
3. Adicionar o user, host, password e port do banco de dados

### Criar o ambiente virtual na pasta home do usuário da aplicação
```
python3 -m venv .virtualenv
```

### Inicializar o ambiente virtual
```
source .virtualenv/bin/activate
```

### Instalar as dependências
```
pip3 install --no-cache-dir -r requirements.txt
```

### Criar as migrações
- *sempre que modificar algum model ou adicionar/remover alguma lib*
```
makemigrations myapp --pythonpath='apps'
python3 manage.py makemigrations auth attachment config django_celery_results notification post_office
```

### Criar o superuser
```
python3 manage.py createsuperuser
```

### Aplicar as migrações no banco de dados
```
python3 manage.py migrate
```

### Importar o dump inicial de dados
```
python3 manage.py loaddata application/fixtures/dump
```

### Criar o usuário do RabbitMQ
- Instale o RabbitMQ! Revise os itens do tópico *Requisitos do Sistema*
- https://stackoverflow.com/questions/40436425/how-do-i-create-or-add-a-user-to-rabbitmq#answer-52295727
```
sudo rabbitmqctl list_users
sudo rabbitmqctl add_user application application
sudo rabbitmqctl set_user_tags application administrator
sudo rabbitmqctl set_permissions -p / application ".*" ".*" ".*"
```

#### Listar filas de mensagens no RabbitMQ
```
sudo rabbitmqctl list_queues
```

#### Limpar uma fila no RabbitMQ
```
sudo rabbitmqctl delete_queue celery
```

#### Reiniciar os VHosts no RabbitMQ
```
sudo rabbitmqctl restart_vhost
```

#### Iniciar o serviço do RabbitMQ
- Linux
```
sudo service rabbitmq-server start
sudo systemctl daemon-reload
```
- Mac
```
sudo rabbitmq-server start
```

### Para enviar email do ambiente local
```
python3 -m smtpd -n -c DebuggingServer localhost:1025
```

### Configure o .env com as variáveis de ambiente para o servidor SMTP local
```
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
```

### Iniciar a aplicação
##### 1. inicie uma instância do celery (async tasks)
```
celery --app application worker -l INFO
```

#### 2. inicie uma instância do Celery beat (schedule tasks)
```
celery --app application beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### 3. inicie o django
```
python3 manage.py runserver 0.0.0.0:8000
```

### Para ver o banco do RabbitMQ
```
sudo rabbitmq-plugins enable rabbitmq_management
http://localhost:15672/
```

### Para atualizar o arquivo de dump (exportar a base de dados para um json)
[Leia aqui mais detalhes sobre o export de dados do Django](https://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django)
```
python3 manage.py dumpdata --natural-foreign --natural-primary -e auth.Permission -e admin.logentry -e contenttypes -e log -e sessions.session -e post_office -e django_celery_results > application/fixtures/dump.json
```

## Para Exportar / Importar o dump MySQL
To export:
```
mysqldump -u mysql_user -p <db_name> > backup.sql
```

To import (importar com root):
```
mysqldump -u root -p <db_name> < backup.sql
```

## Para gerar o certificado via let's encrypt de um site
    sudo certbot --nginx

## Para resetar a base de dados
    mysqldump -u <user> -p <db-name> < <backup.sql>

    mysql> DROP DATABASE <db_name>;
    Query OK, 97 rows affected (1.27 sec)

    mysql> CREATE DATABASE <db_name>;
    Query OK, 1 row affected (0.01 sec)

    mysql> FLUSH PRIVILEGES;
    ERROR 1227 (42000): Access denied; you need (at least one of) the RELOAD privilege(s) for this operation
    mysql>

<br><br>

### Leituras recomendadas
- [Django Design Philosophies](https://docs.djangoproject.com/pt-br/3.2/misc/design-philosophies)
- [Sobre Djando Fixtures - tutorial oficial](https://docs.djangoproject.com/en/3.2/howto/initial-data)
- [Sobre Djando Fixtures - tutorial 1](https://coderwall.com/p/mvsoyg/django-dumpdata-and-loaddata)
- [Sobre Djando Fixtures - tutorial 2](https://getkt.com/blog/how-to-export-and-import-fixtures-in-django)
- [Sobre o uso do UUID como PK no lugar do default INT AutoIncrement](https://stackoverflow.com/questions/3936182/using-a-uuid-as-a-primary-key-in-django-models-generic-relations-impact)
- [Django Post Office](https://github.com/ui/django-post_office)
- [Celery Application](https://docs.celeryproject.org/en/latest/userguide/application.html)
- [Celery Worker](https://docs.celeryproject.org/en/latest/userguide/workers.html)
- [Django Celery](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html)

- Sobre boas práticas de API RESTFul
    - https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design
    - https://www.freecodecamp.org/news/rest-api-best-practices-rest-endpoint-design-examples
    - https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api
    - https://medium.com/@mwaysolutions/10-best-practices-for-better-restful-api-cbe81b06f291
    - Usar sempre JSON como estrutura de dados.
    - Usar substantivos em vez de verbos nos endpoints.
    - Usar coleções de nomes com substantivos no plural (carros, acessorios, grupos etc.).
    - Usar códigos de status do HTTP no tratamento de erros.
        > 400 Bad Request – This means that client-side input fails validation.<br>
        > 401 Unauthorized – This means the user isn’t not authorized to access a resource. It usually returns when the user isn’t authenticated.<br>
        > 403 Forbidden – This means the user is authenticated, but it’s not allowed to access a resource.<br>
        > 404 Not Found – This indicates that a resource is not found.<br>
        > 500 Internal server error – This is a generic server error. It probably shouldn’t be thrown explicitly.<br>
        > 502 Bad Gateway – This indicates an invalid response from an upstream server.<br>
        > 503 Service Unavailable – This indicates that something unexpected happened on server side (It can be anything like server overload, some parts of the system failed, etc.).<br>