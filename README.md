# Bloc4 BCN: Aplicació de reserves

## 1. Resum de l'aplicació

### 1.1 Client i descripció del projecte

El [Bloc4BCN](https://bloc4.coop/) és un projecte públic-cooperatiu finançat per l’Ajuntament de Barcelona i la Generalitat de Catalunya.

El seu propòsit és contribuir al desenvolupament i la transformació socioeconòmica de la ciutat de Barcelona i de tot el territori català a través de la sensibilització i promoció del cooperativisme, la incubació i acceleració de cooperatives, potenciant la intercooperació, la connexió local i internacional i l’aliança amb altres agents culturals, educatius i empresarials.

### 1.2 Objectiu, l'aplicació s'ha de resoldre

### 1.3 Tipus de roles

Actualment, només ni ha dos tipus de roles:

- Usuari administrador: Encarregat de gestionar les reserves, crear usuaris, crear entitats i gestionar els privilegis de les entitats.

- Usuari d'una entitat: Per fer servir l'aplicació de reserves, un usuari ha de pertànyer a una entitat. Tot i que hi ha quatre tipus d'entitats (`EntityTypesChoices`), que tenen descomptes diferents en el preu per hora de la reserva, hi ha dos grups ben diferenciats:

  - Entitat allotjada: Un administrador de Bloc4BCN serà l'encarregada de crear el compte de l'usuari i de l'entitat. Tenen la avantatja de certs privilegis com hores mensuals bonificades al mes per reserva de sales de reunions, hores anuals bonificades per aules o poder reservar aules sense confirmació (tot configurable des del model `EntityPrivilege` al panel Admin).

  Les factures de les reserves d'aquestes entitats, seran mensuals, i per això s'ha implementat en l'apartat "Les teves reserves" un resum del total a pagar amb els descomptes dels bonus gratuïts.

  - Entitat externa: Tenen la particularitat de haver de fer el registre des de l'aplicació, no tindran accés a bonus d'hores gratuïts i han de facturar les reserves individualment.

## 2. Configuració del projecte

1. Descarregar el repositori en el teu ordinador amb `git clone https://github.com/codicoop/bloc4.git`
2. Assegura't que tens instal·lada la versió correcta de Python, comprovant en l'arxiu _docker/Dockerfile_ y el _pyproject.toml_ i haurà de ser la mateixa versió. Després, executa `python -V` en l'arrel, per saber la versió de Python que està fent servir el teu ordinador.
3. Si la versió és diferent, fes servir [Pyenv](https://github.com/pyenv/pyenv) per instal·lar la versió correcta amb el comandament `pyenv local x.xx.xx`
4. Executa `poetry install` i `npm install` en l'arrel, per instal·lar els packages necessaris.
5. Canviar de nom el fitxer docker/.env.example a docker/.env, i acabar d'ajustar variables si és necessari. Per la pujada d'arxius, omplir la part de `Media / Storage` ambs les dades de Wasabi.
6. Si vas a fer canvis en els estils HTML, has de compilar-los perquè es mostrin. Ho fas amb: `npx tailwindcss -i ./src/assets/styles/input.css -o ./src/assets/styles/output.css --watch` des de la consola de Docker: `docker exec -it bloc4-app bash`
7. També des de la consola Docker, executar: `python manage.py migrate`.
8. Entrar a la versió en local a través de: [localhost:1401](http://localhost:1401)

## 3. Stack usat

### 3.1 Backend

- [Python](https://www.python.org/) 3.11
- [Django](https://www.djangoproject.com/) 5.0.3

### 3.2 Frontend

- [TailwindCSS](https://tailwindcss.com/)
- [FlowBite](https://github.com/themesberg/flowbite)
- [Hyperscript](https://hyperscript.org/)
- [HTMX](https://htmx.org/)

### 3.3 Contenidors i altres eines

- Docker
- npm, for Tailwind compilation
- Poetry, a python package manager

## 4. Guia per desenvolupament

#### 4.1 Tesdting, liniting i formateig

Comandaments que cal executar a la carpeta arrel del projecte.

Per validar el linting:

    poetry run ruff check

Per arreglar problemes generals de linting:

    poetry run ruff check --fix

A vegades cal fer:

    poetry run ruff check --fix --unsafe-fixes

En cas de fer això, és encara més important revisar els canvis abans de fer
el commit.

Per formatejar el codi:

    poetry run ruff format

En cas que només vulguis comprovar el format de codi però sense modificar-lo:

    poetry run ruff format --check

Per tirar els tests de python (inclou els de Selenium):

Cal entrar a la consola del contenidor de docker i allà executar:

    python manage.py test
