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

