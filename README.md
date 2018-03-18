# stack-overflow-survey

## Install

Install dependencies with

```bash
pip install -r requirements-freeze.txt
```

## Run

The script runs in two steps:
- Transform raw Stack Overflow survey data using `pandas`
- Plot the data as `bokeh` charts

```bash
python src/main.py transform ../data/2017/survey_results_schema.csv
python src/main.py chart
```

All side effects are sotred in the `generated` folder

## Questions

- Are modern programming languages used by a more diverse group?