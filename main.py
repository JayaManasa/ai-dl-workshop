from fastapi import FastAPI, UploadFile, HTTPException
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, db
import json
from utils import convert_pdf_to_images, process_images_with_gemini

app = FastAPI()

bucket_name = "invoices-from-user"
key_file_path = "./service-account.json"

# Initialize storage client
storage_client = storage.Client.from_service_account_json(key_file_path)
bucket = storage_client.get_bucket(bucket_name)
# initialise firebase
cred = credentials.Certificate("./firebase.json")
firebase_admin.initialize_app(
    cred, {"databaseURL": "https://consciouscart-16d52-default-rtdb.firebaseio.com/"}
)
db = firestore.client()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/api/file")
async def list_files():
    try:
        # Assuming 'bucket' is already initialized somewhere in your code
        blobs = bucket.list_blobs()
        files = []
        for blob in blobs:
            files.append({
                "name": blob.name,
                "created": blob.time_created.isoformat() if blob.time_created else None
            })
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@app.post("/api/upload-file/{user_email}")
async def upload_file(file: UploadFile, user_email: str):
    filename = f"{file.filename}_{user_email}"
    blob = bucket.blob(filename)
    blob.upload_from_file(file.file)
    return {"message": "File uploaded successfully", "filename": filename}

@app.post("/api/create-user/{user_name}")
async def add_user(user_name: str):
    # store the user in the user collection
    return True


# TODO : change products to invoices
"""

CHange the schema of what we store in invoices this way:

    {
        "invoices": ...everything in the product, file_name
    }

{ 
 users: ["harsha": {invoices: [..., file_name]}, "hemanth": {invoices: [.... filename]}]

 users: [..., user: {files: [file_name1, file_name2], invoices:
                     [invoice_output_from_gemini, filename]}]

"""
def exists_in_firebase(file_name):
    ref = db.reference("/invoices") # should be invoices
    invoices = ref.get()
    if not invoices:
        return False
    invoices = invoices.strip("```json")
    invoices = invoices.strip("```")
    invoices = json.loads(invoices)

    if invoices:
        for invoice in invoices:
            # should be file_name
            if invoice['product_name'] == file_name:
                return invoice
    return False

# TODO: Change from products to invoices
@app.get("/api/process/{file_name}")
async def process_file(file_name: str):
    # This is where we check in firebase if the file is processed
    # if file is processed, we retrun the response stored in firebase.

    product_in_firebase = exists_in_firebase(file_name)
    if product_in_firebase:
        return product_in_firebase

    file = bucket.get_blob(file_name)
    if not file:
        return {"errror": "File not found in storage"}

    file_content = file.download_as_bytes()

    # Determine file type
    file_extension = file_name.split('.')[-1].lower()

    # Convert PDF to images if necessary
    if file_extension == 'pdf':
        images = convert_pdf_to_images(file_content)
    else:
        images = [file_content]  # For non-PDF files, treat as single image

    gemini_output = process_images_with_gemini(images)

    # Prepare the data to store in Firebase
    firebase_data = {
        "invoices": gemini_output,
        "file_name": file_name
    }

    # Store the processed data in Firebase
    ref = db.reference("/invoices")
    ref.child(file_name.replace('.', '_')).set(firebase_data)

    return firebase_data


    # extract from gemini
        # get the file from the bucket with the file_name using google cloud
        # send the file contents to gemini prompt
        # get the response and store it in firebase .set() !! WITHOUT OVERRIDING
        # THE EXISING
        # send the response as the output of gemini

    # store in firebase invoices


    ## Then we call the gemini api
    ## step 1:  WE get an output from gemini, store it in firebase
    ## step 2: We return the output to the client
