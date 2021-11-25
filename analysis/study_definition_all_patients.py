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
import pyarrow.feather as feather

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
        (region != '')
        """,
        # Indicator for registration
        registered = patients.registered_as_of("index_date"),
    ),            
    **common_variables
)

######################
#      Measures      #
######################

measures = [
    # Thresholds  
    Measure(
        id = "total_tests_by_dm",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = "diabetes_type",
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = "diabetes_type",
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = "diabetes_type",
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = "diabetes_type",
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = "diabetes_type",
        #small_number_suppression=True,
    ),
    # Demographics (Total)
    Measure(
        id = "total_tests_by_dm_and_age",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","age_group"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "total_tests_by_dm_and_sex",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","sex"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "total_tests_by_dm_and_ethnicity",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","ethnicity"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "total_tests_by_dm_and_region",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","region"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "total_tests_by_dm_and_imd",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","imd"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "total_tests_by_dm_and_ld",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","learning_disability"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "total_tests_by_dm_and_mi",
        numerator = "took_hba1c",
        denominator = "population",
        group_by = ["diabetes_type","mental_illness"],
        #small_number_suppression=True,
    ),
    # Demographics (> 48)
    Measure(
        id = "tests_gt48_by_dm_and_age",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","age_group"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm_and_sex",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","sex"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm_and_ethnicity",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","ethnicity"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm_and_region",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","region"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm_and_imd",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","imd"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm_and_ld",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","learning_disability"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt48_by_dm_and_mi",
        numerator = "hba1c_gt_48",
        denominator = "population",
        group_by = ["diabetes_type","mental_illness"],
        #small_number_suppression=True,
    ),
    # Demographics (> 58)
    Measure(
        id = "tests_gt58_by_dm_and_age",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","age_group"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm_and_sex",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","sex"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm_and_ethnicity",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","ethnicity"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm_and_region",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","region"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm_and_imd",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","imd"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm_and_ld",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","learning_disability"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt58_by_dm_and_mi",
        numerator = "hba1c_gt_58",
        denominator = "population",
        group_by = ["diabetes_type","mental_illness"],
        #small_number_suppression=True,
    ),
    # Demographics (> 64)
    Measure(
        id = "tests_gt64_by_dm_and_age",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","age_group"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm_and_sex",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","sex"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm_and_ethnicity",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","ethnicity"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm_and_region",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","region"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm_and_imd",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","imd"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm_and_ld",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","learning_disability"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt64_by_dm_and_mi",
        numerator = "hba1c_gt_64",
        denominator = "population",
        group_by = ["diabetes_type","mental_illness"],
        #small_number_suppression=True,
    ),
    # Demographics (> 75)
    Measure(
        id = "tests_gt75_by_dm_and_age",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","age_group"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm_and_sex",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","sex"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm_and_ethnicity",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","ethnicity"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm_and_region",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","region"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm_and_imd",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","imd"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm_and_ld",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","learning_disability"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "tests_gt75_by_dm_and_mi",
        numerator = "hba1c_gt_75",
        denominator = "population",
        group_by = ["diabetes_type","mental_illness"],
        #small_number_suppression=True,
    ),
]