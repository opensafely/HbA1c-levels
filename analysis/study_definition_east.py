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
        (region != '') AND
        took_hba1c
        """,
        # Indicator for registration
        registered = patients.registered_as_of("index_date"),
        # Age
        age = patients.age_as_of("index_date"),   
        # Sex
        sex = patients.sex(return_expectations={
            "rate": "universal",
            "category": {"ratios": {"M": 0.49, "F": 0.51}},
        }),     
    ),

    # Index date 
    index_date = "2016-01-01",   

    # Region
    region = patients.registered_practice_as_of(
        "index_date",
        returning = "nuts1_region_name",
        return_expectations = {
            "category": {
                "ratios": {
                    "North East": 0.1,
                    "North West": 0.1,
                    "Yorkshire and the Humber": 0.1,
                    "East Midlands": 0.1,
                    "West Midlands": 0.1,
                    "East of England": 0.1,
                    "London": 0.2,
                    "South East": 0.2, 
                }
            },       
            "incidence": 0.8}
    ),

    # Indicator for East region
    east=patients.satisfying(
        """
        region = 'East'
        """         
    ),

    # Diabetes
    type1_diabetes=patients.with_these_clinical_events(
        diabetes_t1_codes,
        on_or_before="index_date",
        return_last_date_in_period=True,
        include_month=True,
    ),

    type2_diabetes=patients.with_these_clinical_events(
        diabetes_t2_codes,
        on_or_before="index_date",
        return_last_date_in_period=True,
        include_month=True,
    ),

    unknown_diabetes=patients.with_these_clinical_events(
        diabetes_unknown_codes,
        on_or_before="index_date",
        return_last_date_in_period=True,
        include_month=True,
    ),
    
    diabetes_type=patients.categorised_as(
        {
            "T1DM":
                """
                        (type1_diabetes AND NOT
                        type2_diabetes) 
                    OR
                        (((type1_diabetes AND type2_diabetes) OR 
                        (type1_diabetes AND unknown_diabetes AND NOT type2_diabetes) OR
                        (unknown_diabetes AND NOT type1_diabetes AND NOT type2_diabetes))
                        AND 
                        (insulin_lastyear_meds > 0 AND NOT
                        oad_lastyear_meds > 0))
                """,
            "T2DM":
                """
                        (type2_diabetes AND NOT
                        type1_diabetes)
                    OR
                        (((type1_diabetes AND type2_diabetes) OR 
                        (type2_diabetes AND unknown_diabetes AND NOT type1_diabetes) OR
                        (unknown_diabetes AND NOT type1_diabetes AND NOT type2_diabetes))
                        AND 
                        (oad_lastyear_meds > 0))
                """,
            "UNKNOWN_DM":
                """
                        ((unknown_diabetes AND NOT type1_diabetes AND NOT type2_diabetes) AND NOT
                        oad_lastyear_meds AND NOT
                        insulin_lastyear_meds) 
                   
                """,
            "NO_DM": "DEFAULT",
        },

        return_expectations={
            "category": {"ratios": {"T1DM": 0.03, "T2DM": 0.2, "UNKNOWN_DM": 0.02, "NO_DM": 0.75}},
            "rate" : "universal"

        },

        # Patient took antidiabetic drugs
        oad_lastyear_meds=patients.with_these_medications(
            oad_med_codes, 
            between=["index_date - 365 days", "index_date - 1 day"],
            returning="number_of_matches_in_period",
        ),
        # Patient took insulin
        insulin_lastyear_meds=patients.with_these_medications(
            insulin_med_codes,
            between=["index_date - 365 days", "index_date - 1 day"],
            returning="number_of_matches_in_period",
        ),
    ),

    # Indicator for T2DM
    diabetes_t2=patients.satisfying(
        """
        diabetes_type = 'T2DM'
        """         
    ),

    # Indicator for test
    took_hba1c=patients.with_these_clinical_events(
        hba1c_new_codes,
        find_last_match_in_period=True,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="binary_flag",
        return_expectations={
            "incidence": 0.1,
        }
    ), 
    
    # HbA1c Test
    hba1c_mmol_per_mol=patients.with_these_clinical_events(
        hba1c_new_codes,
        find_last_match_in_period=True,
        between=["index_date", "last_day_of_month(index_date)"],
        returning="numeric_value",
        include_date_of_match=True,
        return_expectations={
            "float": {"distribution": "normal", "mean": 40.0, "stddev": 20},
            "incidence": 0.95,
        },
    ),

    prev_hba1c_mmol_per_mol=patients.with_these_clinical_events(
        hba1c_new_codes,
        find_last_match_in_period=True,
        between=["index_date - 15 months", "index_date - 1 day"],
        returning="numeric_value",
        include_date_of_match=True,
        return_expectations={
            "float": {"distribution": "normal", "mean": 40.0, "stddev": 20},
            "incidence": 0.95,
        },
    ),
)

######################
#      Measures      #
######################

measures = [
    # Average HbA1c by region
    Measure(
        id = "avg_hba1c_region",
        numerator = "hba1c_mmol_per_mol",
        denominator = "population",
        group_by = ["diabetes_t2","east"],
        #small_number_suppression=True,
    ),
]