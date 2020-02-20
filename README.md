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
 
## Notes on Sierra Leon:
 - Divided into [5 administrative regions](https://en.wikipedia.org/wiki/Provinces_of_Sierra_Leone)
 - Further divided into [16 Districts](https://en.wikipedia.org/wiki/Districts_of_Sierra_Leone)
 - Further divided into [186 chiefdoms](https://en.wikipedia.org/wiki/Chiefdoms_of_Sierra_Leone)
 - Chiefdoms may be cut into "Sections" ([ref 1](https://www.humanitarianresponse.info/sites/www.humanitarianresponse.info/files/documents/files/ocha_sle_ref_kono_landscape.pdf), [ref2](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_bonthe_landscape.pdf))
 - District maps can be found [here](https://reliefweb.int/updates?source=1503&format=12.12570&advanced-search=(PC211)#content)
 
## Data Notes:
 - Trigger_Ave: I do not believe that Gobaru Li is a Section (associated with ambiguous Chiefdom label).
 - Trigger_Ave: I do not believe that Zombo 11 is a Section, possibly confused with Zoker II?
 - Trigger_Ave: I do not believe that Moindekoh is a Chiefdom or a Section, possibly confused with the Section Moindekor
 - Trigger_Ave: I do not believe that Njakor is a Chiefdom, it may be a Section (but does not appear to be in the Kono district).
 - Trigger_Ave: I do not believe that Njala Komboya is a Chiefdom. Maybe confused with Komboya?
 - Trigger_Ave: I do not believe that Pesseh is a Chiefdom. Maybe confused with Pujehun District, Panga Kabonde Chiefdom, Pesseh Section [ref](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_pujehun_landscape.pdf).
 - Trigger_Ave: I do not believe that Sabaa is a Chiefdom. Maybe confused with Pujehun District, Kpaka Chiefdom, Sarbah Section [ref](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_pujehun_landscape.pdf).
 - Trigger_Ave: Chiefdom Safroko Limba is supposed to be in Bombali District, not Tonkolili District.
 - Trigger_Ave: I do not believe that Sakrim is a Chiefdom.
 - Trigger_Ave: I do not believe that Taama Forest is a Chiefdom.
 - Trigger_Ave: I do not believe that Woefeh is a Chiefdom, and it is not a Section in Kono District.
 - Line 2 of Trigger_Ave: Gbomoti is not a Chiefdom. Don't know how to fix.
 - Line 18 of Trigger_Ave: Bapewa is not a Chiefdom. May be District=Pujehun, Chiefdom=Yakemo Kpukumu Krim (or YKK), Section=Bapewa, Community=Manjama [ref](https://www.bsg.ox.ac.uk/sites/default/files/2018-06/Jones_Perfromance%20Managment%20in%20Sierra%20Leone.pdf)
 - Line 22 of Trigger_Ave: Gbap is not a Chiefdom. May be Chiefdom=Nongoba Bullom, Section=Gbap, Community=? [ref](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_bonthe_landscape.pdf)
 - Line 47 of Trigger_Ave: Gbaama is not a Chiefdom. May be Chiefdom=Soro Gbema, Section=?, Community=?
 - Line 70 of Trigger_Ave: Jassande Keifema is not a Chiefdom. May be District=Pujehun, Chiefdom=Kpaka, Section=Jassende Kpeima, Community=Tokor [ref](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_pujehun_landscape.pdf)
 - Line 70 of Trigger_Ave: Kemoh is not a Chiefdom. Don't know how to fix.
 - Line 287 of Trigger_Ave: Nyango is not a Chiefdom. Don't know how to fix.
 - Line 577 of Trigger_Ave: Ngoleima is not a Chiefdom. May be District=Pujehun, Chiefdom=Kpaka, Section=Jassende Ngoleima, Community=Lahun [ref](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_pujehun_landscape.pdf)
 - Line 1127 of Trigger_Ave: Chepo is not a Chiefdom. May be Chiefdom=Dema, Section=Chepo, Community=Gambia [ref](https://reliefweb.int/sites/reliefweb.int/files/resources/ocha_sle_ref_bonthe_landscape.pdf)
 - Line 1416 of Trigger_Ave: Owawor is not a Chiefdom. Don't know how to fix.
 - Line 1815 of Trigger_Ave: Gbaama is not a Chiefdom. Don't know how to fix.
 - Lines 2296 and 2297 of Trigger_Ave: Seem like they may be data collected for the same region on the same date? Should be combined?
 - Lines 4961 of Trigger_Ave: Mano Dasse is not a Chiefdom. May be Chiefdom=Kagboro, Section=Mano, Community=? or Chiefdom=Dasse, Section=?, Community=? [ref](https://reliefweb.int/map/sierra-leone/sierra-leone-moyamba-district-reference-map-28-july-2015)
 - Line 6496 of Trigger_Ave: Gbayafe is not a Chiefdom. Don't know how to fix.
 - 
 
 