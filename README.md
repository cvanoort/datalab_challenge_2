# Data Lab (CSYS 395, Spring 2020) Challenge #2
- Assigned 2020/02/18
- Due 2020/03/10
- Team 3:
  - Anoob Prakash
  - Jessica Cole
  - Elizabeth Espinosa
  - Erik Brown
  - Samuel Rosenblatt
  - Colin Van Oort


## Problems
 1. Parse the [SMAC data files](https://figshare.com/articles/Social_Mobilization_Action_Consortium_Community_Engagement_data_from_the_2014-2016_Sierra_Leone_Ebola_outbreak/8247002).
 2. Reproduce the analyses from the [SMAC paper](https://www.biorxiv.org/content/10.1101/661959v1).
    - Number of Community Visits time series
    - Burial by Chiefdom and burial type time series
    - Community By-laws time series
 3. Identify surprising chiefdoms: Regions that had a lot more or a lot less cases than neighbors.
 Do they stand-out in social mobilization data?
 4. Continue the exploration in interesting directions:
    - Compare the attack rate in people to the attack rate over chiefdoms.
    - Is there any evidence that misinformation or distrust in the intervention lead to
lower rates of reporting, safe burials and referrals?
    - Are social mobilizers from different organizations getting similar ratings in the
different evaluation metrics?

## Solutions
 1.
 2.
 3.
 4.

## Resources
 - [Dataset](https://figshare.com/articles/Social_Mobilization_Action_Consortium_Community_Engagement_data_from_the_2014-2016_Sierra_Leone_Ebola_outbreak/8247002)
 - [Paper 1](https://www.biorxiv.org/content/10.1101/661959v1)
 - [Paper 2](https://www.pnas.org/content/113/16/4488)
 
## Notes on Sierra Leone:
 - Divided into [5 administrative regions](https://en.wikipedia.org/wiki/Provinces_of_Sierra_Leone)
 - Further divided into [16 Districts](https://en.wikipedia.org/wiki/Districts_of_Sierra_Leone)
 - Further divided into [186 chiefdoms](https://en.wikipedia.org/wiki/Chiefdoms_of_Sierra_Leone)
 - Chiefdoms may be cut into "Sections" ([ref 1](https://www.humanitarianresponse.info/sites/www.humanitarianresponse.info/files/documents/files/ocha_sle_ref_kono_landscape.pdf), [ref2](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_bonthe_landscape.pdf))
 - District maps can be found [here](https://reliefweb.int/updates?source=1503&format=12.12570&advanced-search=(PC211)#content)
 
## Repo Notes:
 - When looking at the column discrepancies that are output by `etl.py`, it can 
   be useful to combine multiple related discrepancy files with the following 
   command:
    ```bash
    cat *.json | sed 's/,//g' | grep -v -E '\[|\]' | sort | uniq 
    ```
   In particular, you can reduce the globbing to a category of interest, such as `cat *Chiefdoms.json ...`.