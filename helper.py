import boto3

import time
import requests
import json
import uuid
import IPython
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont

def upload_and_get_url(bucket_name, key, audio,region_name):
    
    s3 = boto3.client('s3',region_name=region_name)

    request = {
        "Bucket" : bucket_name,
        "Key" : key,
        "Body" : audio
    }

    result = s3.put_object(**request)
    
    url = s3.generate_presigned_url(
        ClientMethod='get_object', 
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600)

    return url

def get_text_from_transcription_job(result):
    text = ''
    if result['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        job_uri = result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        r = requests.get(job_uri)
        text = r.json()['results']['transcripts'][0]['transcript']
    return text

def wait_for_job(job_name,transcribe):
    
    result = ''
    loop = True
    while loop:
        loop = False

        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if result['TranscriptionJob']['TranscriptionJobStatus']=='FAILED':
            print("Transcription job failed")
            print(result['TranscriptionJob']['FailureReason'])
            return result

        if result['TranscriptionJob']['TranscriptionJobStatus'] == 'IN_PROGRESS':
            print('Job not done yet. Waiting 30 seconds...')
            time.sleep(30)
            loop = True
    return result

def display_image(bucket_name,photo,region_name):    # Load image from S3 bucket
    s3_connection = boto3.resource('s3',region_name=region_name)
    print(region_name)
    print(bucket_name)
    bucket = s3_connection.Bucket(bucket_name)

    s3_object = bucket.Object(photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)
    return image



def display_image_custom(bucket_name,photo,response,region_name):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3',region_name=region_name)

    bucket = s3_connection.Bucket(bucket_name)

    s3_object = bucket.Object(photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    if 'CustomLabels' in response:
    # calculate and display bounding boxes for each detected custom label
    
        print('Detected custom labels for ' + photo)

        for customLabel in response['CustomLabels']:
            print('Label ' + str(customLabel['Name']))
            print('Confidence ' + str(customLabel['Confidence']))
            if 'Geometry' in customLabel:
                box = customLabel['Geometry']['BoundingBox']
                left = imgWidth * box['Left']
                top = imgHeight * box['Top']
                width = imgWidth * box['Width']
                height = imgHeight * box['Height']

                #fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 50)
                draw.text((left,top), customLabel['Name'], fill='#00d400')


                points = (
                    (left,top),
                    (left + width, top),
                    (left + width, top + height),
                    (left , top + height),
                    (left, top))
                draw.line(points, fill='#00d400', width=5)

    return image

def display_image_text(bucket_name,photo,response,threshold,region_name):
    # Load image from S3 bucket
    s3_connection = boto3.resource('s3',region_name)

    bucket = s3_connection.Bucket(bucket_name)

    s3_object = bucket.Object(photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response['Body'].read())
    image=Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    if 'TextDetections' in response:
    # calculate and display bounding boxes for each detected custom label
    
        print('Detected text for ' + photo)

        for customLabel in response['TextDetections']:
            
            if customLabel['Confidence'] > threshold:

                if 'Geometry' in customLabel:
                    box = customLabel['Geometry']['BoundingBox']
                    left = imgWidth * box['Left']
                    top = imgHeight * box['Top']
                    width = imgWidth * box['Width']
                    height = imgHeight * box['Height']

                    points = (
                        (left,top),
                        (left + width, top),
                        (left + width, top + height),
                        (left , top + height),
                        (left, top))
                    draw.line(points, fill='#00d400', width=5)

    return image