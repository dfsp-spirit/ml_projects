# wahlomat-analysis


This directory contains some python3 script to perform some basic analyses of the Wahl-o-mat data. The [whal-o-mat](https://www.wahl-o-mat.de) is a voting advice application made available by the German [Bundeszentrale für politische Bildung](http://www.bpb.de/).


## What is Wahl-o-mat?

A number of statements about important topics are given to all political parties before elections, and the parties can provide whether they agree or disagree with each statement (they can also say neutral). People who use the Wahl-o-mat also answer the statements, and can then compare their own answers to those given by the parties.

## Where does the data come from?

The script `get_data.bash` retrieves them from the [qual-o-mat-data repository by gockelhahn](https://github.com/gockelhahn/qual-o-mat-data) here on github.

## What do the scripts do?

They perform cluster analysis to compute a similarity between the parties (two parties are considered similar when they answered to the statements in a similar way) and the statements (two statements are similar if the pattern of answers to them by the parties are similar).

Here is an example for Europawahl 2019 in Germany:


The colors mean:
* Red: party disagreed with statement
* Green: party agreed
* Gray: neutral

![Clustering](./clustering_parties_statements.png?raw=true "Clustering of parties and statements for Europawahl 2019 in Germany")


## What does this tell me?

**How to read the image:** Note that to see the similarities, what you should look at are the cluster dendrograms (on the left for the parties, and at the top for the statements), not at the ordering of parties! (E.g., the answers of the *FDP* are way more similar to *Die Humanisten* than to *Bündnis C.*, even though it is adjacent to *Bündnis C* in the ordering.)

One can use the image to position parties by their answers, or to find blocks of similar parties:

* For a small party which you do not know much about, you can see how close its answers were to those from other parties you know. E.g., one can see that the answers of *Volksabstimmung* are most similar to those given by the right-wing extremist party NPD, and that the answers given by *Ökolinx* are most similar to those given by *Die Linke*.

* You can also see how similar the answers of a number of parties are to each other. For example, there is a large block of left-wing parties (in the lower third of the figure) which have given very similar answers to most questions.

* You can see which parties are specialist parties that only care for certain topics. E.g., *Gesundheitsforschung* gave a neutral answer to all statements except the one concerning animal experiments.

## Limits

Of course, the Wahl-o-mat idea is not without issues, and this analysis adds some more.

The statements force parties to answer complex political questions with yes or no, and the questions themselves may be biased. And of course, two parties can give the same answer for entirely different reasons. So take this with a grain of salt and at least read the comments from the parties, which are also available in the data. In these comments, they explain *why* they answered in a certain way.
