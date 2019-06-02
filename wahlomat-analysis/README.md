# wahlomat-analysis


This directory contains some python3 script to perform some basic analyses of the Wahl-o-mat data. The [whal-o-mat](https://www.wahl-o-mat.de) is a voting advice application made available by the German [Bundeszentrale für politische Bildung](http://www.bpb.de/).


## What is Wahl-o-mat?

A number of statements about important topics are given to all political parties before elections, and the parties can provide whether they agree or disagree with each statement (they can also say they do not have an opinion on it). People who use the Wahl-o-mat also answer the statements, and can then compare their own answers to those given by the parties.

## Where does the data come from?

The script `get_data.bash` retrieves them from the [qual-o-mat-data repository by gockelhahn](https://github.com/gockelhahn/qual-o-mat-data) here on github.

## What do the scripts do?

They perform cluster analysis to compute a similarity between the parties (two parties are considered similar when they agree on many statements) and the statements (two statements are similar if the pattern of answers to them by the parties are similar).

Here is an example:
![Clustering](./clustering_parties_statements.png?raw=true "Clustering of parties and statements for Europawahl 2019 in Germany")
