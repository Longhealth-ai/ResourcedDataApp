import json
import fhirclient.models.patient as p
import fhirclient.models.encounter as e
import fhirclient.models.documentreference as dr
import psycopg2
import configparser

# use configparser to parse config file
config = configparser.ConfigParser()
config.read("app/config.ini")

host = config['DEFAULT']['host']
port = config['DEFAULT']['port']
database = config['DEFAULT']['database']
user = config['credentials']['user']
password = config['credentials']['password']

# Load the patient JSON
# with open("Resourcejsons/Patient.json", 'r') as h:
#     pjs = json.load(h)
# complete_json = json.dumps(pjs)
#
# # Create a Patient object from the JSON
# patient = p.Patient(pjs)

def patient_data_parser(pjs):
    complete_json = json.dumps(pjs)
    patient = p.Patient(pjs)
    # Extract patient information
    try:
        patient_id = patient.id
    except (IndexError, AttributeError):
        patient_id = "null"
    try:
        given_name = patient.name[0].given[0]
    except (IndexError, AttributeError):
        given_name = "null"
    # print("name: ",patient.name)
    try:
        family_name = patient.name[0].family
    except (IndexError, AttributeError):
        family_name = "null"
    # print(family_name)
    try:
        gender = patient.gender
    except (IndexError, AttributeError):
        gender = "null"
    # print(gender)
    try:
        birth_date = patient.birthDate.isostring
    except (IndexError, AttributeError):
        birth_date = "null"
    # print(birth_date)
    try:
        medical_record_number = patient.identifier[0].value
    except (IndexError, AttributeError):
        medical_record_number = "null"
    # print(medical_record_number)
    # Connect to the PostgreSQL database
    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        cursor = connection.cursor()
        # print("connection created successfully")
        # Insert patient data into the table
        insert_query = '''
            INSERT INTO patients_new (id, given_name, family_name, gender, birth_date, medical_record_number,complete_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        cursor.execute(insert_query, (patient_id, given_name, family_name, gender, birth_date, medical_record_number, complete_json))

        connection.commit()
        # print("Record inserted successfully")
        return True
    except (Exception, psycopg2.Error) as error:
        # print("Error:", psycopg2.Error.mro())
        return False


def encounter_data_parser(pjs,patient_id):
    complete_json = json.dumps(pjs)
    encounter_data = pjs['entry']
    connection = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    cursor = connection.cursor()
    # print("connection created successfully")

    for data in encounter_data:
        try:
            encounter_id = data['resource']['id']
        except (IndexError, AttributeError, KeyError):
            encounter_id = "null"
        # print("encounter id : ", encounter_id)
        try:
            status = data['resource']["status"]
        except (IndexError, AttributeError, KeyError):
            status = "null"
        # print("status: ", status)
        try:
            class_data = data['resource']['class']['display']
        except (IndexError, AttributeError, KeyError):
            class_data = "null"
        # print("class_data : ", class_data)
        try:
            subject_reference = str(data['resource']['subject'])
        except (IndexError, AttributeError, KeyError):
            subject_reference = "null"
        # print("subject_reference : ", subject_reference)
        try:
            service_type = data['resource']['serviceType']['text']
        except (IndexError, AttributeError, KeyError):
            service_type = "null"
        # print("servicetype : ", service_type)
        try:
            individual_participant = data['resource']['participant']
            if len(individual_participant) > 0:
                individuals = str([participant["individual"] for participant in individual_participant])
        except (IndexError, AttributeError, KeyError):
            individuals = "null"
        # print("individuals : ", individuals)
        try:
            period = data['resource']['period']['start']
        except (IndexError, AttributeError, KeyError):
            period = "null"
        # print("period : ", period)

        try:
            insert_query = '''
              INSERT INTO encounter (encounterid, status, classdata, subjectreference, servicetype, individualparticipant, period, patientid, complete_json)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
            # print("data insertion in progress")
            cursor.execute(insert_query, (
                encounter_id, status, class_data, subject_reference, service_type, individuals, period, patient_id, complete_json))

            connection.commit()
            # print("Encounter Data inserted successfully")
        except (Exception, psycopg2.Error) as error:
            # print("Error:", error)
            return False
    return True

def document_reference_data_parser(pjs,patient_id):
    complete_json = json.dumps(pjs)
    ref_data = pjs['entry']

    connection = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    cursor = connection.cursor()
    # print("connection created successfully")

    for data in ref_data:
        try:
            ref_id = data['resource']['id']
        except (IndexError, AttributeError, KeyError):
            ref_id = "null"
        # print("refe id : ", ref_id)
        try:
            status = data['resource']["status"]
        except (IndexError, AttributeError, KeyError):
            status = "null"
        # print("status: ", status)
        try:
            docstatus = data['resource']["docStatus"]
        except (IndexError, AttributeError, KeyError):
            docstatus = "null"
        # print("status: ", docstatus)
        try:
            doctype = data['resource']["type"]["text"]
        except (IndexError, AttributeError, KeyError):
            doctype = "null"
        # print("status: ", doctype)
        try:
            category = data['resource']['category']
            if len(category) > 0 :
                cate = category[0]['text']
            else:
                cate = "null"
        except (IndexError, AttributeError, KeyError):
            cate = "null"
        try:
            subject_reference = str(data['resource']['subject'])
        except (IndexError, AttributeError, KeyError):
            subject_reference = "null"
        # print("subject_reference : ", subject_reference)
        try:
            insert_query = '''
                     INSERT INTO documentreference (docid, status, docstatus, doctype, category, subjectreference, patientid, complete_json)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                   '''
            # print("data insertion in progress...")
            cursor.execute(insert_query, (
                ref_id, status, docstatus, doctype, cate, subject_reference, patient_id, complete_json))

            connection.commit()
            # print("document reference Data inserted successfully")
        except (Exception, psycopg2.Error) as error:
            # print("Error:", error)
            return False
    return True

def observation_data_parser(pjs,patient_id):
    complete_json = json.dumps(pjs)
    obs_data = pjs['entry']

    connection = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    cursor = connection.cursor()
    # print("connection created successfully")

    for data in obs_data:
        try:
            obs_id = data['resource']['id']
        except (IndexError, AttributeError, KeyError):
            obs_id = "null"
        # print("obs id : ", obs_id)
        try:
            status = data['resource']["status"]
        except (IndexError, AttributeError, KeyError):
            status = "null"
        # print("status: ", status)
        try:
            category = data['resource']['category']
            if len(category) > 0 :
                cate = category[0]['text']
            else:
                cate = "null"
        except (IndexError, AttributeError, KeyError):
            cate = "null"
        try:
            subject_reference = str(data['resource']['subject'])
        except (IndexError, AttributeError, KeyError):
            subject_reference = "null"
        # print("subject_reference : ", subject_reference)
        try:
            effective_datetime = data['resource']['effectiveDateTime']
        except (IndexError, AttributeError, KeyError):
            effective_datetime = "null"
        # print("effective_datetime : ", effective_datetime)
        try:
            issued = data['resource']['issued']
        except (IndexError, AttributeError, KeyError):
            issued = "null"
        # print("issued : ", issued)
        try:
            insert_query = '''
            INSERT INTO observation (observationid, status, category, subjectreference, effectivedatetime, issued, patientid, complete_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            '''

            # print("data insertion in progress...")
            cursor.execute(insert_query, (
                obs_id, status, cate, subject_reference, effective_datetime, issued, patient_id, complete_json))

            connection.commit()
            # print("observation Data inserted successfully")
        except (Exception, psycopg2.Error) as error:
            # print("Error:", error)
            return False
    return True
