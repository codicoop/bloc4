# Bloc4 BCN - Espai Cooperatiu

# Installation guide
In order to install this project, you have to:

1. Import the project.
2. In the root, you have to install the packages necessaries with `npm install`
3. After, if you are going to make changes in the html styles, you have to compile them in order for them to show. You do it with:
`npx tailwindcss -i ./src/assets/styles/input.css -o ./src/assets/styles/output.css --watch`
4. Inside */docker/* folder rename **.env.example** to **.env** and then run  `docker compose up`.
5. From Docker shell ejecute: `python manage.py migrate`.
6. Go to: [localhost:1401](http://localhost:1234)
7. **.env** creates a superuser account with username hola@codi.coop
