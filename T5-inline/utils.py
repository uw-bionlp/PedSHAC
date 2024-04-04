note_descrition="clinical note social history section for pediatric patients"
ADOPTION = 'Adoption'
EDUCATION_ACCESS = 'Education_access'
LIVING_ARRANGEMENT= 'Living_arrangement'
EMPLOYMENT = 'Employment'
FOOD_INSECURITY= 'Food_insecurity'
PRIOR_TRAUMA = 'Prior_trauma'
MENTAL_HEALTH = 'Mental_health'
ALCOHOL = 'Alcohol'
TOBACCO = 'Tobacco'
DRUG = 'Drug'
Trigger_type=[ADOPTION,EDUCATION_ACCESS,LIVING_ARRANGEMENT,EMPLOYMENT,FOOD_INSECURITY,
   PRIOR_TRAUMA,MENTAL_HEALTH,ALCOHOL,TOBACCO,DRUG ]

id2label={0:"O"}
for key in Trigger_type:
    id2label[len(id2label)]="I-"+key
    id2label[len(id2label)]="B-"+key
label2id={}
for key in id2label:
    label2id[id2label[key]]=key


STATUS               = "Status"

EUDCATION_STATUS = 'Education_Status'

LIVING_STATUS = 'Living_Status'
LIVING_TYPE ='Living_Type'
RESIDENCE ='Residence'

EMPLOYMENT_STATUS = 'Employment_Status'

FOOD_STATUS = 'Food_Status'

PRIOR_STATUS = 'Prior_Status'
PRIOR_TYPE = 'Prior_Type'

MENTAL_STATUS = 'Mental_Status'
MENTAL_EXPERIENCER= 'Mental_Experiencer'

SUBSTANCE_STATUS = 'Substance_Status'
SUBSTANCE_EXPERIENCER ='Substance_Experiencer'
SUBSTANCE_TYPE = 'Substance_Type'
AMOUNT='Amount'
FREQUENCY='Frequency'

# For Education_StatusVal
YES = 'yes'
NO = 'no'

# For Living_StatusVal
CURRENT = 'current'
PAST = 'past'
FUTURE = 'future'

# For Living_TypeVal
WITH_BOTH_PARENTS = 'with_both_parents'
WITH_SINGLE_PARENT = 'with_single_parent'
WITH_OTHER_RELATIVES = 'with_other_relatives'
WITH_STRANGERS = 'with_strangers'
WITH_FOSTER = 'with_foster'

# For ResidenceVal
HOME = 'home'
INSTITUTION = 'institution'
HOMELESS = 'homeless'

# For Employment_StatusVal
EMPLOYED = 'employed'
UNEMPLOYED = 'unemployed'
RETIRED = 'retired'
ON_DISABILITY = 'on_disability'
STUDENT = 'student'
HOMEMAKER = 'homemaker'

# For Food_StatusVal
NONE = 'none'  # Repeated, might want to consider renaming to avoid conflict

# For Prior_StatusVal
# YES and NO already defined

# For Prior_TypeVal
DIVORCE_SEPARATION = 'divorce_separation'
LOSS = 'loss'
PSYCHOLOGICAL = 'psychological'
PHYSICAL = 'physical'
DOMESTIC_VIOLENCE = 'domestic_violence'
SEXUAL = 'sexual'

# For Mental_StatusVal
# NONE, CURRENT, PAST already defined

# For Mental_ExperiencerVal
PATIENT = 'patient'
PARENT_CAREGIVER = 'parent_caregiver'

SUBTYPES_BY_ARGUMENT = {
    EUDCATION_STATUS:[YES,NO],  
    LIVING_STATUS:[CURRENT,PAST,FUTURE],
    LIVING_TYPE:[WITH_BOTH_PARENTS,WITH_FOSTER,WITH_OTHER_RELATIVES,WITH_SINGLE_PARENT,WITH_STRANGERS],
    RESIDENCE:[INSTITUTION,HOME,HOMELESS],
    EMPLOYMENT_STATUS:[EMPLOYED,UNEMPLOYED,RETIRED,ON_DISABILITY,STUDENT,HOMEMAKER],
    FOOD_STATUS:[CURRENT,PAST,NONE],
    PRIOR_STATUS:[YES,NO],
    PRIOR_TYPE:[DIVORCE_SEPARATION,LOSS,PHYSICAL,PSYCHOLOGICAL,DOMESTIC_VIOLENCE,SEXUAL],
    MENTAL_STATUS:[CURRENT,PAST,NONE],
    MENTAL_EXPERIENCER:[PATIENT,PARENT_CAREGIVER],
    SUBSTANCE_STATUS:[NONE,CURRENT,PAST],
    SUBSTANCE_EXPERIENCER:[PATIENT,PARENT_CAREGIVER]
    }
    
ARGUMENTS_BY_EVENT_TYPE = {
    ADOPTION:[],
    EDUCATION_ACCESS: [EUDCATION_STATUS],
    LIVING_ARRANGEMENT: [LIVING_STATUS, LIVING_TYPE, RESIDENCE],
    EMPLOYMENT: [EMPLOYMENT_STATUS],
    FOOD_INSECURITY: [FOOD_STATUS],
    PRIOR_TRAUMA: [PRIOR_STATUS, PRIOR_TYPE],
    MENTAL_HEALTH: [MENTAL_STATUS, MENTAL_EXPERIENCER],
    ALCOHOL: [SUBSTANCE_STATUS, SUBSTANCE_EXPERIENCER],
    TOBACCO: [SUBSTANCE_STATUS, SUBSTANCE_EXPERIENCER],
    DRUG: [SUBSTANCE_STATUS, SUBSTANCE_EXPERIENCER]
}
choices=['A','B','C','D','E','F','G','H','I']

# important tags list https://www.geeksforgeeks.org/python-part-of-speech-tagging-using-textblob/
desired_tags=['FW',
              'JJ',
              'NN',
              'RB',
              'RP',
              'VB']