#Snag-Brendan-a-Job 1.0
#Programming language: Python 3.7.3

import json
import os

#PURPOSE: Validate one or more JOBAPPLICATION files against a QUESTIONLIST file to identify accepted applications.
#         In order to be accepted, a jobapplication file must:
#               1.  Conform to JSON specifications
#               2.  Include the applicant name
#               3.  Include an acceptable answer to every question specified in the questionlist file.  

#SETUP:  Prior to executing the script, the following steps must be taken
#       1. File api_code_assignment_config.json (JSON) must be created in the same directory that the script is running in.
#       2. The config file must specify the directory containing the job application files (jobApplicationDirectory").
#       3. The config file must specify the name of the question list file ("questionListFile").
#       4. The questionlistfile must be located in the same directory as the script

#INPUTS:  None

#OUTPUT:  Display the applicant name and path of the application for valid (Accepted) applications.
#         If there are no accepted applications, a message indicating that will be displayed instead

#ASSUMPTIONS:

#   Assumption 1:  Every question specified in the questionlist file has a unique question id (i.e. "id1", "id2", etc)
#   Assumption 2:  To be evaluated, the number of answers in the jobapplication file MUST match the number of questions in the questionlist file.
#   If the number of answers is LESS THAN the number of questions, it's impossible for there to be a valid answer for every question -> UNACCEPTABLE.
#   If the number of answers is GREATER THAN the number of questions, it is POSSIBLE that there is a valid answer for every question.
#   However, it's also possible that there are different answers to the same question  -> UNACCEPTABLE.

#   Assumption 3:  The evaluation is case-agnostic (The answer "Python" is evaluated the same as the answer "PYTHON")

#   Assumption 4:  The spelling of an answer must EXACTLY MATCH the spelling of an acceptable answer for the corresponding question.
#                  Example: If the only acceptable answer to a question is "Python", "Piethon" is NOT acceptable.
#                  To workaround this limitation, there is flexibility to define ANY NUMBER of acceptable answers to a question in the questionlist file
#                      #Example: "Python", "Piethon", "Pithon", "Python2", "Python3", etc)

#END OF ASSUMPTIONS

#Function FN_find_job_application_answer
#Purpose: For a specified Question ID, search the specified answerlist for an answer.
#Parameters: Question ID (string), Answer List (list)
#Returns: A string containing the Answer, or NONE if no answer was found

def FN_find_job_application_answer ( strQuestionID, lstApplicantAnswers ) :
    for objApplicantAnswer in lstApplicantAnswers :
        if ( objApplicantAnswer.get ('Id') == strQuestionID ) :
            strApplicantAnswer=objApplicantAnswer.get('Answer')
            return strApplicantAnswer
    return None #An answer to this question wasn't found in the answer list

#END of FN_find_job_application_answer

# Function FN_validate_job_application
# Purpose: Evaluates an application against a question list.
# Parameters: Application (Dictionary Object), Question List (list object)
# Returns: True if application is valid, False if not

def FN_validate_job_application (  dctJobApplication,lstQuestionList ):
   
    #First, make sure the Name (Applicant Name) is included in the Job Application
    #This is a requirement
    strApplicantName=dctJobApplication.get('Name')

    if strApplicantName == None :
        #"Applicant name missing from application, unacceptable application
        return False
    lstApplicantAnswers=dctJobApplication.get('Questions')

    if lstApplicantAnswers == None:
        #No answers found, unacceptable applicationfile
        return False

    #Confirm the number of answers in the jobapplication matches the number of questions in the questionlist
    #If not, unacceptable application

    if len(lstApplicantAnswers) != len(lstQuestionList) :
        return False

    #Iterate through the questions in the questionlist, comparing each question to the corresponding answer in the answerlist
    for objQuestion in lstQuestionList :

        boolValidAnswer=False  #By default, the answer is unacceptable until proven otherwise
        strQuestionID=objQuestion.get("Id")  #Get the QuestionID for this question
        objValidAnswerList=objQuestion.get("Answer") #Get the list of acceptable answers for this question

        strApplicantAnswer=FN_find_job_application_answer ( strQuestionID, lstApplicantAnswers ) #Look for the answer to the question in the answerlist

        #If any of questions are unanswered, application is unacceptable
        if ( strApplicantAnswer == None ):
            return False 
                       
        #Iterate through the acceptable answers to this question, checking if any of them match the application answer

        for strValidAnswer in objValidAnswerList:
        #Comparison is case-agnostic
            if ( strValidAnswer.upper() == strApplicantAnswer.upper() ):
                boolValidAnswer=True
        #If we couldn't find an acceptable answer to this question, we don't need to evaluate any more questions, the application is not acceptable
        if ( boolValidAnswer == False ) :
            return False
                           
    #If acceptable answers were found for all questions in the questionlist, return True (acceptable application)
    return True

#END of FN_validate_job_application

#############################
#MAIN
#############################

strConfigFile="api_code_assignment_config.json"

#The configuration file specifies the name of the question list file, and the directory path of the applications to be evaluated

try:
    
    with open (strConfigFile,"r") as read_file:
        dctConfigData=json.load(read_file)

except OSError as err:
    print("OS Error opening config file, make sure it exits: {0}".format(err))
    quit()

except json.decoder.JSONDecodeError as err:
    print("JSON Error reading config file, make sure its a valid JSON schema: {0}".format(err))
    read_file.close()
    quit()

read_file.close()

strQuestionListFile=dctConfigData.get ('questionListFile')
strJobApplicationDirectory=dctConfigData.get ('jobApplicationDirectory')

#Make sure the questionlist file is specified in the config file

if strQuestionListFile == None :
    print ("Please specify questionListFile in " +strConfigFile)
    exit()

#Make sure the application directory is defined in the config file

if strJobApplicationDirectory == None :
    print ("Please specify jobApplicationDirectory in config file to specify applications to be processed")
    exit()

#Open the question list file and load into a dictionary object

try:
    with open (strQuestionListFile,"r") as question_list_file:
        dctQuestions=json.load(question_list_file)
except OSError as err:
    print ("OS Error opening questionlist file, make sure it exists: {0}".format(err))
    quit()
except json.decoder.JSONDecodeError as err:
    print("JSON Error reading questionlist file, make sure its a valid JSON schema: {0}".format(err))
    question_list_file.close()
    quit()

question_list_file.close()

#Get the list of questions from the question list file

lstQuestions=dctQuestions.get('questions') #Get the question list

if ( lstQuestions == None ) :
    print ("No questions found, please make sure at least one question is specified in "+strQuestionListFile)
    exit()

print ("Processing " + strJobApplicationDirectory + " using question list file " + strQuestionListFile)

#Make sure the ApplicationDirectory exists
if not os.path.exists(strJobApplicationDirectory):
    print ("Application directory "+ strJobApplicationDirectory+" not found, please check "+strApplicationDirectory + " in app_config.json")
    exit()

lstValidApplications = list()

for applicationFile in os.listdir(strJobApplicationDirectory):

    #Find the path to the job application file
    #Rename strApplication to strJobApplication, because "Application" could refer to a program and that's confusing
    strJobApplicationFilePath=strJobApplicationDirectory+"\\"+applicationFile

    #If the Job Application file has an invalid JSON schema, it will be considered unacceptable
    
    boolValidApplicationFileJSONSchema=False
        
    try:
        with open (strJobApplicationFilePath,"r") as read_file:
            dctJobApplicationData=json.load(read_file)
        read_file.close()
        boolValidApplicationFileJSONSchema=True
    
    except json.decoder.JSONDecodeError as err:
        read_file.close()

    if ( boolValidApplicationFileJSONSchema == True ):
        boolValidJobApplication=FN_validate_job_application (  dctJobApplicationData,lstQuestions )

        if ( boolValidJobApplication == True ) :
            lstValidApplications.append(applicationFile)
            
#END for loop

if ( len (lstValidApplications) == 0 ) :
    print ("Processing complete, no valid applications found")
else :
    lstValidApplications.sort();
    print ("Processing complete: list of valid applications:")
    for strValidApplication in lstValidApplications:
        print (strValidApplication)


