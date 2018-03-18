import argparse
import pandas as pd
import json
import math
import logging
import os

from bokeh.io import save, output_file
from bokeh.plotting import figure, ColumnDataSource
from bokeh.layouts import row
from bokeh.models import HoverTool


# Map functions
def languages(language_list):
  """
  Return a delimited list of languages as seperated boolean columns
  """
  try:
    return {k: True for k in language_list.split('; ')}
  except AttributeError:
    return {}

def percentagise(series, k):
  """
  Return a ratio of one row in the series compared to the sum total
  """
  p = series[k] / series.sum()
  return p

# serde
def generate_csv(df, filename):
  return df.to_csv(os.path.join("generated", filename), header=True)

# Command functions
def transform_data(args):
  """
  Transform raw csv data to computed csv data
  """

  # Read in languages by year data
  df_timeline = pd.read_csv(
    os.path.join("meta", "timeline_clean.csv"),
    header=None,
    names=['LanguageAppeared', 'Language']
  )
  df_timeline.set_index('Language', inplace=True)

  # Read in survey data
  df = pd.read_csv(args.infile)

  # Spread 'have worked in' languages out into boolean columns
  df_languages = df['HaveWorkedLanguage'].map(languages).apply(pd.Series)
  # join back onto 'gender'
  df_joined = pd.concat([df['Gender'], df_languages], axis=1)

  #print("Original records and languages:")
  #print(df_joined.head())

  # Count each language field by gender
  df_summary = df_joined.groupby(['Gender']).count()
  #print("Languages summarised by gender:")
  #print(df_summary.iloc[:5, :5])

  # Generate Series of '% Male' figures by language
  df_percentage = df_summary.apply(percentagise, axis=0, args=('Male', )).to_frame('Male')
  # Generate Series of 'Total' figures for each language
  df_total = df_languages.apply(lambda x: x.count()).to_frame('Total')

  #print(df_percentage.head())
  
  df_percentage = df_percentage.join(df_total).join(df_timeline)
  # Warn here if we have NaN values brought in from our timeline dataframe
  #print("WARN Missing language years:")
  #print(df_percentage.loc[df_percentage['LanguageAppeared'].isnull()])
  df_percentage['LanguageAppeared'] = df_percentage['LanguageAppeared'].astype(int)

  df_percentage = df_percentage.reset_index()
  df_percentage.rename(columns={'index':'Language', 0:'Male'}, inplace=True)
  print("Transformed data head:")
  print(df_percentage.head())

  # Write out computed data
  # general summary
  generate_csv(df_summary, "summary.csv")
  # percentage gender by language
  generate_csv(df_percentage, "percentage.csv")
  # all languages found in the data
  generate_csv(df_percentage['Language'], "languages.csv")


def chart_data(args):
  """
  Turn computed data to a chart
  """
  # Data formatting
  df_percentage = pd.read_csv(os.path.join("generated", "percentage.csv"))
  df_percentage.sort_values(
    'Male',
    axis=0,
    ascending=False,
    inplace=True,
    kind='quicksort',
    na_position='last'
  )
  output_file(os.path.join("generated", "index.html"))
  lang = df_percentage['Language'].values
  perc = [x * 100 for x in df_percentage['Male'].values]
  appe = df_percentage['LanguageAppeared'].values
  magn = [math.log(x, 10) / 2 for x in df_percentage['Total'].values]
  perc_avg = sum(perc)/len(perc)
  colors = list(map(lambda x: '#CC0000' if x < perc_avg else '#00CC00', perc))

  # Bar plot
  p = figure(
    x_range=lang,
    plot_height=600,
    plot_width=600,
    title="% Male by Language",
    y_range=(70, 100),
  )
  p.vbar(
    x=lang,
    top=perc,
    bottom=perc_avg,
    width=0.9,
    fill_color=colors,
    line_color=None,
  )
  p.xgrid.grid_line_color = None
  p.xaxis.major_label_orientation = math.pi/3
  p.y_range.start = 0

  # Scatter plot
  source = ColumnDataSource(data=dict(
    x=appe,
    y=perc,
    desc=lang,
    r=magn
  ))
  hover = HoverTool(tooltips=[
    ("Year Appeared", "@x"),
    ("% Male", "@y"),
    ("Language", "@desc"),
  ])
  q = figure(
    plot_height=600,
    plot_width=600,

    title="% Male by Language Appeared Year"
  )
  q.add_tools(hover)
  q.circle('x', 'y', radius='r', color="navy", alpha=0.5, source=source)

  save(row(p, q))


def main_parser():
  parser = argparse.ArgumentParser('stack-overflow-survey')
  subparsers = parser.add_subparsers()

  parser_transform = subparsers.add_parser('transform', help='compute stats')
  parser_transform.add_argument('infile', help='2017 SO data infile (survey_results_schema.csv)')
  parser_transform.set_defaults(func=transform_data)
  parser_chart = subparsers.add_parser('chart', help='chart stats')
  parser_chart.set_defaults(func=chart_data)

  return parser

def main():
  parser = main_parser()
  args = parser.parse_args()
  
  if hasattr(args, 'func'):
    args.func(args)
  else:
    parser.print_help()

if __name__ == "__main__":
  main()
