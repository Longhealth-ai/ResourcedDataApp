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
from .PatientParser import patient_data_parser


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


def index(request):
    Accesstoken = Generate_Token()
    if request.method == 'POST':
        patientid = request.POST['patientid']

        # Get Patient API call
        patient_api = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/{patientid}"

        # check if token is valid
        token_valid_invalid = checkiftokenisvalid(Accesstoken,patientid)
        if token_valid_invalid.status_code==200:
            json_data = token_valid_invalid.text
            json_obj = json.loads(json_data)
            value = patient_data_parser(json_obj)
            print("value: ", value)
            if value:
                messages.success(request,f'Patient Record Inserted Successfully')
            else:
                print("unsuccessfull")
            messages.success(request, 'Access token is valid!!')
        else:
            print(token_valid_invalid.status_code)
            messages.error(request, 'Access token is invalid!!')
    return render(request,"index.html")