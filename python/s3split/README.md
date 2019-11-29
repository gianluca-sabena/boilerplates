# s3split

## Run

- Activate env `pipenv shell`
- Install dependencies `pipenv install`
- Run main `python src/s3split.py -h`
- Run tests `pytest`

## Dev

- Install dev dependencies `pipenv install --dev`
- Created with `pipenv --python 3.7`
- Add a dev dependency `pipenv install pytest --dev`
- Packages and directory layout:
  - Separate src and test dir <https://docs.pytest.org/en/latest/goodpractices.html?highlight=directory%20layout#tests-outside-application-code> 
  - see also a suggested link <https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure>
  - python package <https://docs.python.org/3.7/tutorial/modules.html#packages>
- console script <https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html>
- Not required anymore... ~~Add an empty file `touch src/conftest.py` to instruct pytest to add src dir to sys.path <https://stackoverflow.com/a/50156706/7568979>~~