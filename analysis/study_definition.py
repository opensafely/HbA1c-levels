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
    
    # Index date for comparison
    index_date = "2019-01-01",
    
    # Sex
    sex = patients.sex(return_expectations={
        "rate": "universal",
        "category": {"ratios": {"M": 0.49, "F": 0.51}},
    }),
    
    # Limiting to patients who had an HbA1c test 
    population=patients.satisfying(
        """
        took_hba1c AND 
        registered AND
        (sex = 'M' OR sex = 'F')
        """,
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
        # Indicator for registration
        registered = patients.registered_as_of("index_date"),
    ),
                       
    # Age
    age_group = patients.categorised_as(
        {
            "0-15": "age >= 0 AND age < 16",
            "16-24": "age >= 16 AND age < 25",
            "25-34": "age >= 25 AND age < 35",
            "35-44": "age >= 35 AND age < 45",
            "45-54": "age >= 45 AND age < 55",
            "55-64": "age >= 55 AND age < 65",
            "65-74": "age >= 65 AND age < 75",
            "75+": "age >= 75",
            "missing": "DEFAULT",
        },
        return_expectations = {
            "rate": "universal",
            "category": {
                "ratios": {
                    "0-15": 0.2,
                    "16-24": 0.1,
                    "25-34": 0.1,
                    "35-44": 0.15,
                    "45-54": 0.1,
                    "55-64": 0.1,
                    "65-74": 0.1,
                    "75+": 0.13,
                    "missing": 0.02,
                }
            },
        },
        age = patients.age_as_of(
            "index_date",
        ),
    ),
                       
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
    
    # Index of multiple deprivation
    imd = patients.categorised_as(
        {
            "0": "DEFAULT",
            "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
            "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
            "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
            "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
            "5": """index_of_multiple_deprivation >= 32844*4/5 """,
        },
        index_of_multiple_deprivation = patients.address_as_of(
            "index_date",
            returning = "index_of_multiple_deprivation",
            round_to_nearest = 100,
        ),
        return_expectations = {
            "rate": "universal",
            "category": {
                "ratios": {
                    "0": 0.01,
                    "1": 0.20,
                    "2": 0.20,
                    "3": 0.20,
                    "4": 0.20,
                    "5": 0.19,
                }
            },
        },
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
    
    # Indicators for diabetes type
    diabetes_t1=patients.categorised_as(
        {
            '0':'DEFAULT', 
            '1': 
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
                    """
        },
        return_expectations={
            "category": {"ratios": {"0": 0.97, "1": 0.03}},
            "rate" : "universal"
        },
        
    ),
    
    diabetes_t2=patients.categorised_as(
        {
            '0':'DEFAULT', 
            '1': 
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
        },
        return_expectations={
            "category": {"ratios": {"0": 0.8, "1": 0.2}},
            "rate" : "universal"
        },
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
    
    # Flag abnormal results        
    hba1c_abnormal=patients.categorised_as(
        {"0": "DEFAULT", "1": """hba1c_mmol_per_mol >= 42"""},
        return_expectations = {"rate": "universal",
                              "category": {
                                  "ratios": {
                                      "0": 0.94,
                                      "1": 0.06,
                                      }
                                  },
                              },
    ),
    
    # Psychosis
    psychosis_schiz_bipolar=patients.with_these_clinical_events(
        psychosis_schizophrenia_bipolar_affective_disease_codes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01, },
    ),
    
    # Depression
    depression=patients.with_these_clinical_events(
        depression_codes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01, },
    ),
    
    # Dementia
    dementia=patients.with_these_clinical_events(
        dementia_codes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.02, },
    ),
    
    # Learning disabilities
    learning_disability=patients.with_these_clinical_events(
        learning_disability_codes,
        on_or_before="index_date",
        returning="binary_flag",
        return_expectations={"incidence": 0.01, },
    ),
    
    # Mental illness
    mental_illness=patients.categorised_as(
        {"None": "DEFAULT", 
         "Severe Mental Illness": """(psychosis_schiz_bipolar OR dementia) AND NOT 
                      (depression)""",
         "Depression": """depression AND NOT 
                          (psychosis_schiz_bipolar OR dementia)"""
        },
        return_expectations = {"rate": "universal",
                              "category": {
                                  "ratios": {
                                      "None": 0.93,
                                      "Severe Mental Illness": 0.02,
                                      "Depression": 0.05,
                                      }
                                  },
                              },
    
    ),
                               
)

#############
#  Measure  #
#############    
    
measures = [
    # All test takers
    Measure(
        id = "hba1c_abnormal",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "population",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_diabetes_type",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by="diabetes_type",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_sex",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "sex",
        #small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_age",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "age_group",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_region",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "region",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_imd",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "imd",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_ethnicity",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "ethnicity",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_mental_illness",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "mental_illness",
        small_number_suppression=True,
    ),
    Measure(
        id = "hba1c_abnormal_by_learning_disability",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = "learning_disability",
        small_number_suppression=True,
    ),
    # T1 Diabetes Only
    Measure(
        id = "t1dm_hba1c_abnormal",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by="diabetes_t1",
        small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_sex",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["sex","diabetes_t1"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_age",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["age_group","diabetes_t1"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_region",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["region","diabetes_t1"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_imd",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["imd","diabetes_t1"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_ethnicity",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["ethnicity","diabetes_t1"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_mental_illness",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["mental_illness","diabetes_t1"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t1dm_hba1c_abnormal_by_learning_disability",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["learning_disability","diabetes_t1"],
        small_number_suppression=True,
    ),
    # T2 Diabetes Only
    Measure(
        id = "t2dm_hba1c_abnormal",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by="diabetes_t2",
        small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_sex",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["sex","diabetes_t2"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_age",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["age_group","diabetes_t2"],
        #small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_region",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["region","diabetes_t2"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_imd",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["imd","diabetes_t2"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_ethnicity",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["ethnicity","diabetes_t2"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_mental_illness",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["mental_illness","diabetes_t2"],
        small_number_suppression=True,
    ),
    Measure(
        id = "t2dm_hba1c_abnormal_by_learning_disability",
        numerator = "hba1c_abnormal",
        denominator = "population",
        group_by = ["learning_disability","diabetes_t2"],
        small_number_suppression=True,
    ),
]
