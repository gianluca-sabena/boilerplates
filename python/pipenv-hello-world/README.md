# Hello world

## Create new project

- Create new project `pipenv --python 3.7`
- Add a dev dependency `pipenv install pytest --dev`
- Separate src and test dir <https://docs.pytest.org/en/latest/goodpractices.html?highlight=directory%20layout#tests-outside-application-code>
- Add an empty file `touch src/conftest.py` to instruct pytest to add src dir to sys.path <https://stackoverflow.com/a/50156706/7568979>

## Run

- Activate env `pipenv shell`
- Run main `python src/main.py --name example`
- Run tests `pytest`

## Dev

- Install dev dependencies `pipenv install --dev`
