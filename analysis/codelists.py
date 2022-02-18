from cohortextractor import (codelist, codelist_from_csv, combine_codelists)

# Diabetes
diabetes_t1_codes = codelist_from_csv(
    "codelists/opensafely-type-1-diabetes.csv", system="ctv3", column="CTV3ID"
)

diabetes_t2_codes = codelist_from_csv(
    "codelists/opensafely-type-2-diabetes.csv", system="ctv3", column="CTV3ID"
)

diabetes_unknown_codes = codelist_from_csv(
    "codelists/opensafely-diabetes-unknown-type.csv", system="ctv3", column="CTV3ID"
)

# Prediabetes 
prediabetes_codes = codelist_from_csv(
    "codelists/opensafely-prediabetes-snomed.csv", system='snomed', column='id'
)

# Ethnicity
ethnicity_codes = codelist_from_csv(
        "codelists/opensafely-ethnicity.csv",
        system="ctv3",
        column="Code",
        category_column="Grouping_6",
)

# HbA1c
hba1c_new_codes = codelist(["XaPbt", "Xaeze", "Xaezd"], system="ctv3")

# Insulin medication
insulin_med_codes = codelist_from_csv(
    "codelists/opensafely-insulin-medication.csv", 
    system="snomed", 
    column="id"
)

# Antidiabetic drugs
oad_med_codes = codelist_from_csv(
    "codelists/opensafely-antidiabetic-drugs.csv",
    system="snomed",
    column="id"
)

# Learning disabilities
learning_disability_codes = codelist_from_csv(
    "codelists/opensafely-learning-disabilities.csv",
    system="ctv3",
    column="CTV3Code",
)

# Mental illness codes
psychosis_schizophrenia_bipolar_affective_disease_codes = codelist_from_csv(
    "codelists/opensafely-psychosis-schizophrenia-bipolar-affective-disease.csv",
    system="ctv3",
    column="CTV3Code",
)

depression_codes = codelist_from_csv(
    "codelists/opensafely-depression.csv",
    system="ctv3",
    column="CTV3Code",
)

dementia_codes = codelist_from_csv(
    "codelists/opensafely-dementia-complete.csv", 
    system="ctv3", 
    column="code"
)