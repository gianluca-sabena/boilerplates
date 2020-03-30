# Voila

Voila <https://voila.readthedocs.io/> transforms a notebook in a standalone web application

Requirements:

- Jupyter notebook (jupyter lab is not supported at the moment)
- Jupyter widgets <https://ipywidgets.readthedocs.io/>
- Matplotlib jupyter <https://github.com/matplotlib/jupyter-matplotlib#installation>

## Run

- Install everything with `pipenv install`
- Run notebook `pipenv run jupyter notebook`
- Open voila at <http://localhost:8888/voila>

## Convert notebook 
- run `pipenv run voila <path-to-notebook> <options>`

## Image mouse click

Works with matlib and widget

- Events handling <https://matplotlib.org/3.1.1/users/event_handling.html>