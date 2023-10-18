- [Welcome :star2:](#welcome-star2)
- [Platform Motivation](#platform-motivation)
  - [The Value of Tidy Data :books:](#the-value-of-tidy-data-books)
  - [Why Standardised Plate Reader Protocols Matter :zzz:](#why-standardised-plate-reader-protocols-matter-zzz)
- [How it works :crystal\_ball:](#how-it-works-crystal_ball)
- [How to use it :muscle:](#how-to-use-it-muscle)
  - [Main Dashboard](#main-dashboard)
  - [Submitting New Lysate Batch Data](#submitting-new-lysate-batch-data)
    - [Expression on the Plate Reader](#expression-on-the-plate-reader)
    - [Connecting Labstep](#connecting-labstep)
    - [Uploading Data](#uploading-data)
- [FAQs :sos:](#faqs-sos)
- [Dev and Maintence Docs](#dev-and-maintence-docs)


# Welcome :star2:

I hope that this section has all the information you need to use this platform. If there's something that you think that's been left out, let Alex, Nadanai or some other nerd know and we'll put it in :relaxed:

# Platform Motivation

The purpose of this platform is store and display expression and manufacturing metadata about Lysate CFPS system batches in a way that is:

* Standardised
* Annotated
* Comparable
* Intelligable
* Informative


It is in fact only the last component of a greater data system (comprising of Labstep, the plate reader and this Dashboard). Hence, uploading your data here is the final step in the pipeline which allows your data to be meaningful in the context of other batches. I.e. all that work you did entering Sonication and OD600 data into the Labstep protocol is about to pay off :money_with_wings:

It's often said in Data Science that *"Data Scientists spend up to 80% of the time on data cleaning and 20 percent of their time on actual data analysis"*. Cell-Free Gods willing, this platform will do all of the fiddly dataset cleaning and tidying for you and allow you to spend less time squinting at error messages and more time in the pub generating ideas. It also means that the data will be processed, calibrated and annotated in the same way as everyone else's. :beer:


## The Value of Tidy Data :books:

At the core of the Dashboard is database that stores the data in the tabular ***tidy*** format. This means that it looks like an excel spreadsheet where each possible variable in the dataset (e.g. Lysate Batch Name, RFUs or Harvest OD600 of the batch) has it's own column and each observation forms a row. As a result, this can mean that many more rows are needed to encode the information and Tidy datasets can become quite large in comparison to their raw counterparts. 

So what are the benefits in presenting data in this way? Most data analysis tools in the data-science-verse are designed to expect tidy data (such as Pandas, Matplotlib, Seaborn in Python and ggplot, dplyr and bioconductor in R) and getting your data into this format is a necessary first step in most data analysis processes. 

As mentioned before, each variable has its own column and in that case of plate reader timecourse data this includes *Well* and *Time* so when this data is in the Tidy format, each observation/row consists of only one well at each timepoint as well all of the rest of the associated metadata.

## Why Standardised Plate Reader Protocols Matter :zzz:

I know, I know it's boring but if you could suppress your yawn for moment, I'll be as brief as I can. It's essentially for two reasons: raw data export format and measurement method.

At the time of writing, the dashboard preprocessing scripts can recognise one format of raw data. Whilst it's conceivable that a general artifical AI could be trained to process data whatever format it arrives in, I'm under strict instructions from Nadanai not to get sidetracked into feature request blackholes of side projects.

However there are certain benefits to the standard protocol in that:
1. Only the relevant wells are measured :white_check_mark:
2. The assay itself is standardised rendering different batches of lysate comparable from a data collection standpoint. :cop:
   It would be a shame to discover in a few years that the reason someone was getting no signal compared to the others is that they were using a different orbital shake speed or gain setting.
3. The raw data is exported with all of the information about the assay included meaning you don't have to spend many clicks entering it and removes the possibility of human error. :bath:


# How it works :crystal_ball:

# How to use it :muscle:

## Main Dashboard

## Submitting New Lysate Batch Data

These instructions carry on from the end of the Labstep Lysate Preparation Experiment Protocol and will guide you through:

* Assaying your lysate batch
* Exporting the data
* Creating a labstep inventory record for your batch and connecting the experiment protocol
* Uploading your data to the dashboard

### Expression on the Plate Reader

### Connecting Labstep

### Uploading Data


# FAQs :sos:

# Dev and Maintence Docs


