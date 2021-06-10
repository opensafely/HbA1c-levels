import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Import measures
def import_df(f_path):
    df = pd.read_csv("output/{}.csv".format(f_path))
    # Create percent of population
    df['pct'] = df['value']*100
    return df

# Create charts
def create_chart(measure, ylabel, group, df):
    plt.figure(figsize = (15,8))
    if group=='population':
        ax = sns.lineplot(x = 'date', y = measure, data = df)
    else:
        ax = sns.lineplot(x = 'date', y = measure, hue = group, data = df)
    locs, labels = plt.xticks()
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.setp(labels, rotation=65)
<<<<<<< Updated upstream
    if measure == 'hba1c_abnormal':
=======
    if measure != "pct":
>>>>>>> Stashed changes
        plt.savefig('output/descriptive_counts_{}.png'.format(group))
    else:
        plt.savefig('output/descriptive_pct_{}.png'.format(group))
    
# Dataframes
df_pop = import_df('measure_hba1c_abnormal')
<<<<<<< Updated upstream
=======
df_dm = import_df('measure_hba1c_abnormal_by_diabetes_type')
>>>>>>> Stashed changes
df_sex = import_df('measure_hba1c_abnormal_by_sex')
df_age = import_df('measure_hba1c_abnormal_by_age')
df_region = import_df('measure_hba1c_abnormal_by_region')
df_imd = import_df('measure_hba1c_abnormal_by_imd')

### Absolute measure

# Population
create_chart('hba1c_abnormal', 'Abnormal hBA1c Results (Counts)', 
             'population', df_pop)

<<<<<<< Updated upstream
=======
# Diabetes type
create_chart('hba1c_abnormal', 'Abnormal hBA1c Results (Counts)', 
             'diabetes_type', df_dm)

>>>>>>> Stashed changes
# Sex
create_chart('hba1c_abnormal', 'Abnormal hBA1c Results (Counts)',
             'sex', df_sex)

# Age
create_chart('hba1c_abnormal', 'Abnormal hBA1c Results (Counts)',
             'age_group', df_age.loc[df_age.age_group != 'missing'])

# Region
create_chart('hba1c_abnormal', 'Abnormal hBA1c Results (Counts)',
             'region', df_region)

# Region
create_chart('hba1c_abnormal', 'Abnormal hBA1c Results (Counts)',
             'imd', df_imd)

### Percentage of population

<<<<<<< Updated upstream
# Sex
create_chart('value', 'Abnormal hBA1c Results (% of Population)',
             'sex', df_sex)

# Age
create_chart('value', 'Abnormal hBA1c Results (% of Population)',
             'age_group', df_age.loc[df_age.age_group != 'missing'])

# Region
create_chart('value', 'Abnormal hBA1c Results (% of Population)',
             'region', df_region)

# IMD
create_chart('value', 'Abnormal hBA1c Results (% of Population)',
=======
# Diabetes type
create_chart('pct', 'Abnormal hBA1c Results (% of Population)', 
             'diabetes_type', df_dm)

# Sex
create_chart('pct', 'Abnormal hBA1c Results (% of Population)',
             'sex', df_sex)

# Age
create_chart('pct', 'Abnormal hBA1c Results (% of Population)',
             'age_group', df_age.loc[df_age.age_group != 'missing'])

# Region
create_chart('pct', 'Abnormal hBA1c Results (% of Population)',
             'region', df_region)

# IMD
create_chart('pct', 'Abnormal hBA1c Results (% of Population)',
>>>>>>> Stashed changes
             'imd', df_imd)
