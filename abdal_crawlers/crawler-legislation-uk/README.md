# crawler-legislation-uk
a crawler for extracting all available acts in https://www.legislation.gov.uk/


## All available Data in legislation.gov.uk:
* All Acts : extracted from https://www.legislation.gov.uk/all page
* All Type : extracted from https://www.legislation.gov.uk/search page
* Title : extracted from act page
    * extract options:
      * act page
* Year : extracted from ac each act url
    * all extract options:
      * act url
      * act page
* Type : extracted from ac each act url
    * all extract options:
      * act url
      * act page

* Geographical Extent : extracted from act page
* whole act as txt and pdf : extracted from act page
* Explanatory Note : extracted from act page
* Language : only extracting English (other language is Welsh. Contains only 20 acts, we don't need it :/ )
* Number : extracted from ac each act url
    * all extract options:
      * act url
      * act page
* Numbering system : default numbering system is used
* references to other acts : extracted from act page (work in progress)



## Exported excels
* acts details
* short-type to complete-type 
* acts relations


## Notice
* File pages_loaded.txt is used to store last processed acts so that it would be possible to continue from where we left in case of interruption.
* combination of type , year and number columns in acts.xlsx is unique therefore used as primary key . so if you what to get the file for an act with values eudn (as type), 2020 (as year) and 2252 (as number) you would find it at 
  * extracted_data/files/eudn#2020#2252.pdf for act pdf
  * extracted_data/files/eudn#2020#2252.xht for act xht
  * extracted_data/files/eudn#2020#2252#note.pdf for note pdf
  * extracted_data/files/eudn#2020#2252#note.xht for note xht
* links are saved in refs.xlsx without any preprocess.
