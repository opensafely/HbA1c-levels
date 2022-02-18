#####################
# Import statements #
#####################

from cohortextractor import (
    StudyDefinition,
    patients,
    codelist_from_csv,
    codelist,
    filter_codes_by_category,
    combine_codelists,
    Measure,
)

from common_variables import (
    common_variables
)

from codelists import *

######################
#  Study definition  #
######################

# Define start and end dates

study = StudyDefinition(
    
    # Set time period
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.2,
    },
    
    # Limiting to patients who had an HbA1c test 
    population=patients.satisfying(
        """
        registered AND
        (sex = 'M' OR sex = 'F') AND
        (age >= 16 AND age <= 110) AND
        (diabetes_type != 'UNKNOWN_DM') AND
        (region != '') AND 
        (prev_elevated_48 OR prepandemic_prediabetes)
        """,
        # Indicator for registration
        registered = patients.registered_as_of("index_date"),
    ),        
    prepandemic_hba1c = patients.with_these_clinical_events(
        hba1c_new_codes,
        find_last_match_in_period=True,
        on_or_before="2020-03-01", # approx. pandemic start
        returning="numeric_value",
        return_expectations={
            "float": {"distribution": "normal", "mean": 40.0, "stddev": 20},
            "incidence": 0.95,
        },
    ),  
    prev_elevated_48 = patients.satisfying(
            """
            prepandemic_hba1c > 48
            """
        ),
    prev_elevated_58 = patients.satisfying(
            """
            prepandemic_hba1c > 58
            """
        ),
    prev_elevated_64 = patients.satisfying(
            """
            prepandemic_hba1c > 64
            """
        ),
    prev_elevated_75 = patients.satisfying(
            """
            prepandemic_hba1c > 75
            """
        ),
    prepandemic_prediabetes = patients.with_these_clinical_events(
        prediabetes_codes,
        find_last_match_in_period=True,
        on_or_before="2020-03-01", # approx. pandemic start,
        returning="binary_flag",
        return_expectations={
            "incidence": 0.05,
        }
    ),  
    **common_variables
)