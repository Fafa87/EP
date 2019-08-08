===========
CHANGE LOG:
===========

`1.20`
-------------------------
* option to specify size of the ignored border - those objects are automatically marked as faculatative
* evaluate_frame script which can evaluate a single pair of results-ground truth files so it can be easily used in feedback loop
* option to customize the markers in details overlays
* more flexible and consistent frame number extraction

`1.10`
-------------------------
* python 3 compatibility
* proper CI setup
* additional 'better' formatted report
* png are now loaded for evaluation details
* label or masked images can now be used in evaluation:
    * threshold IOU to accept match defined in INI
    * IOU between matched objects saved in evaluation details

`1.01` 
-------------------------
* compatible with Ubuntu
* universal endline handling
* minor bugs

`1.00`
-------------------------
* errors tracking (in csv and png)
* long term tracking
* should work with both ; and ,
* major refactor
* bug fixes
* minor bug fixes
* summary to std
* report.csv of F values
* segmentation and tracking evaluation details go to file
* visualisation of the evaluation on input images (segmentation, tracking, long tracking)
* long-term tracking evaluation
