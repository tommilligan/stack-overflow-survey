#!/bin/bash

set -e

# Get data source from wikipedia
curl --silent 'https://en.wikipedia.org/w/index.php?title=Timeline_of_programming_languages&action=raw' | \

# Filter for the start of each table
pcre2grep -M '\|-\n\| \d{4}\n\| \[\[.+?\]\]' "../data/Timeline of programming languages.wiki" | \

# Multiline strip wiki markup syntax -> csv
perl -0777 -i -pe 's/\|-\n\| (\d+)\n\| .*(?:\[\[|\|)([^\]]+)\]\]/$1,$2/g' 

