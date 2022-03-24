# Modeling resilient cyber-physical processes and their composition from digital twins via Markov Decision Processes

Code for the submission 
"Modeling resilient cyber-physical processes and their composition from digital twins via Markov Decision Processes".

## Repo structure

- `stochastic_service_composition`: the library; reusable software components of the code.
- [`docs/notebooks/01-electric-motor-production.ipynb`](https://github.com/luusi/stochastic-service-composition-with-ltlf-goals/blob/main/docs/notebooks/01-electric-motor-production.ipynb):
  link to the notebook showing the use case described in the paper.

## Preliminaries

- Set up the virtual environment. 
First, install [Pipenv](https://pipenv-fork.readthedocs.io/en/latest/).
Then:
```
pipenv install --dev
```

- Install the Python package in development mode:
```
pip install -e .
# alternatively:
# python setup.py develop 
```

- To use rendering functionalities, you will also need to install Graphviz. 
  At [this page](https://www.graphviz.org/download/) you will
  find the releases for all the supported platform.

- Follow the instructions to setup [Logaut](https://github.com/whitemech/logaut) with [Lydia](github.com/whitemech/lydia.git) 

## Notebooks

To run the notebooks, activate the virtual environment. Then:

```
jupyter-notebook
```

Then via the browser go to `docs/notebooks` to open the notebooks.

## Docs

To build the docs: `mkdocs build`

To view documentation in a browser: `mkdocs serve`
and then go to [http://localhost:8000](http://localhost:8000)

## License

`stochastic-service-composition-with-ltlf-goals` is released under the MIT license.

Copyright 2022 Luciana Silo
