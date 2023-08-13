import json
import fhirclient.models.patient as p
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
    print(patient_id)
    try:
        given_name = str([patient.name[0].given[0] if patient.name[0].given else "null"][0])
    except (IndexError, AttributeError):
        given_name = "null"
    print(given_name)
    try:
        family_name = patient.name[0].family
    except (IndexError, AttributeError):
        family_name = "null"
    print(family_name)
    try:
        gender = patient.gender
    except (IndexError, AttributeError):
        gender = "null"
    print(gender)
    try:
        birth_date = patient.birthDate.isostring
    except (IndexError, AttributeError):
        birth_date = "null"
    print(birth_date)
    try:
        medical_record_number = patient.identifier[0].value
    except (IndexError, AttributeError):
        medical_record_number = "null"
    print(medical_record_number)
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
        print("connection created successfully")
        # Insert patient data into the table
        insert_query = '''
            INSERT INTO patients_new (id, given_name, family_name, gender, birth_date, medical_record_number,complete_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        cursor.execute(insert_query, (patient_id, given_name, family_name, gender, birth_date, medical_record_number, complete_json))

        connection.commit()
        print("Record inserted successfully")

    except (Exception, psycopg2.Error) as error:
        print("Error:", error)
        return False

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection closed")
    return True
