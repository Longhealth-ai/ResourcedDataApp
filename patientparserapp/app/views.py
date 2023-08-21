from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from datetime import datetime, date
import json
import jose.jwt
import jose
import requests
import uuid
import datetime
from .GenerateToken import checkiftokenisvalid
from django.http import HttpResponseRedirect
from .Parser import patient_data_parser,encounter_data_parser,document_reference_data_parser,observation_data_parser


# Create your views here.

def Generate_Token():
    time = datetime.datetime.now() + datetime.timedelta(minutes=4)
    expiration_time = int(time.timestamp())

    jwt_claims = {
        "iss": "5cc32c7e-4ebb-40f4-99c6-276cfea127d5",  # e26336e4-7cd4-4834-b76b-9673f683d463
        "sub": "5cc32c7e-4ebb-40f4-99c6-276cfea127d5",
        "aud": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
        "exp": expiration_time,
        "jti": uuid.uuid1().__str__()
    }
    newHeaders = {
        "alg": "RS384",
        "typ": "JWT",
        "kid": "kid"
    }

    with open('app/privatekey.pem', 'rb') as fh:
        rsa_signing_jwk = fh.read()
        x = jose.jwt.encode(jwt_claims, rsa_signing_jwk, algorithm='RS384', headers=newHeaders)
        headers = newHeaders
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': x
        }
        x = requests.post('https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token', headers=headers, data=data)
        Access_Token = x.json().get('access_token')
        return Access_Token

def GetPatientdata(accesstoken,patientid):
    patient_api = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/{patientid}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {accesstoken}',
        'Accept': 'application/json',
        'conte': '',
        'Cookie': 'EpicPersistenceCookie=!UYS/HOqzsI6xHurN7uVzAFWOSgxFnHYjcFndXrfIQY+xmG6QN4eJSxGr8xOkL+2iI1l0dEkHzVB42BE=; MyChartLocale=en-US'
    }
    response = requests.request("GET", patient_api, headers=headers, data=payload)
    if response.status_code == 200:
        text_data = response.text
        json_obj = json.loads(text_data)
        if patient_data_parser(json_obj):
            print("data inserted successfully in patient")
            return True
        else:
            print("some problem occured in patient")
    else:
        print("Please enter valid patient id for patient")

def GetEncounterdata(accesstoken,patientid):
    patient_api = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Encounter?patient={patientid}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {accesstoken}',
        'Accept': 'application/json',
        'conte': '',
        'Cookie': 'EpicPersistenceCookie=!UYS/HOqzsI6xHurN7uVzAFWOSgxFnHYjcFndXrfIQY+xmG6QN4eJSxGr8xOkL+2iI1l0dEkHzVB42BE=; MyChartLocale=en-US'
    }
    response = requests.request("GET", patient_api, headers=headers, data=payload)
    if response.status_code == 200:
        text_data = response.text
        json_obj = json.loads(text_data)
        if encounter_data_parser(json_obj,patientid):
            print("data inserted successfully in encounter")
            return True
        else:
            print("some problem occured in encounter")
    else:
        print("Please enter valid patient id for encounter")

def GetDocumentReferencedata(accesstoken,patientid):
    patient_api = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/DocumentReference?patient={patientid}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {accesstoken}',
        'Accept': 'application/json',
        'conte': '',
        'Cookie': 'EpicPersistenceCookie=!UYS/HOqzsI6xHurN7uVzAFWOSgxFnHYjcFndXrfIQY+xmG6QN4eJSxGr8xOkL+2iI1l0dEkHzVB42BE=; MyChartLocale=en-US'
    }
    response = requests.request("GET", patient_api, headers=headers, data=payload)
    if response.status_code == 200:
        text_data = response.text
        json_obj = json.loads(text_data)
        if document_reference_data_parser(json_obj,patientid):
            print("data inserted successfully in document reference")
            return True
        else:
            print("some problem occured in document reference")
    else:
        print("Please enter valid patient id for document reference")


def GetObservationdata(accesstoken,patientid):
    patient_api = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Observation?patient={patientid}&code=8310-5"
    payload = {}
    headers = {
        'Authorization': f'Bearer {accesstoken}',
        'Accept': 'application/json',
        'conte': '',
        'Cookie': 'EpicPersistenceCookie=!UYS/HOqzsI6xHurN7uVzAFWOSgxFnHYjcFndXrfIQY+xmG6QN4eJSxGr8xOkL+2iI1l0dEkHzVB42BE=; MyChartLocale=en-US'
    }
    response = requests.request("GET", patient_api, headers=headers, data=payload)
    if response.status_code == 200:
        text_data = response.text
        json_obj = json.loads(text_data)
        if observation_data_parser(json_obj,patientid):
            print("data inserted successfully in observation")
            return True
        else:
            print("some problem occured in observation")
    else:
        print("Please enter valid patient id for observation")


def index(request):
    SuccessMessages = {}
    if request.method == 'POST':
        Accesstoken = Generate_Token()
        patientid = request.POST['patientid']

        # Get Patient API call

        # check if token is valid
        token_valid_invalid = checkiftokenisvalid(Accesstoken,patientid)
        if token_valid_invalid:
            SuccessMessages['Access_Token'] = "Access token is valid!!"
            patient_data = GetPatientdata(Accesstoken,patientid)
            if patient_data:
                SuccessMessages['Patient'] = "Patient Details inserted successfully"
            else:
                SuccessMessages['Patient'] = "Please enter valid patient ID"
            encounter_data = GetEncounterdata(Accesstoken,patientid)
            if encounter_data:
                SuccessMessages['Encounter'] = "Encounter Details inserted successfully"
            else:
                SuccessMessages['Encounter'] = "Please enter valid patient ID"
            document_reference = GetDocumentReferencedata(Accesstoken,patientid)
            if document_reference:
                SuccessMessages['DocumentRefernce'] = "Document reference data inserted successfully"
            else:
                SuccessMessages['DocumentRefernce'] = "Please enter valid patient ID"
            observation = GetObservationdata(Accesstoken,patientid)
            if observation:
                SuccessMessages['observation'] = "observation data inserted successfully"
            else:
                SuccessMessages['observation'] = "Please enter valid patient ID"

        else:
            SuccessMessages['Accesstoken'] = "Access token is invalid!!"
            print(SuccessMessages['Accesstoken'])

        print(SuccessMessages)
    return render(request,"index.html",{'successmessages': SuccessMessages})
