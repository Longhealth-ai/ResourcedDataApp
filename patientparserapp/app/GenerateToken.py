import requests
def checkiftokenisvalid(Accesstoken,patientid):
    url = f"https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/{patientid}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {Accesstoken}',
        'Accept': 'application/json',
        'Cookie': 'EpicPersistenceCookie=!cZC74rvgDN1BJMPN7uVzAFWOSgxFnCC3itsfNG04Zb2EH8BCR4DEBGLfs1xQUjqwPOCdu1XffKM9KYA=; MyChartLocale=en-US'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response
