
# coding: utf-8

# In[ ]:




import os

import google.oauth2.credentials

import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
import json

from pprint import pprint

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret_app.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def print_response(response):
    print(response)

# Build a resource based on a list of properties given as key-value pairs.
# Leave properties with empty values out of the inserted resource.


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource

# Remove keyword arguments that are not set


def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def comment_threads_list_by_video_id(client, **kwargs):
    # See full sample for function
    kwargs = remove_empty_kwargs(**kwargs)

    response = client.commentThreads().list(
        **kwargs
    ).execute()

    return response


if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    client = get_authenticated_service()

    with open('gafford_videoIds.txt', 'r') as infile:
        video_ids = infile.readlines()

    comment_data = {}

    for item in video_ids:

        content = comment_threads_list_by_video_id(
            client, part='snippet,replies', videoId=item)

        item_id = str(item).strip('\n')

        # ['items']['snippet']['topLevelComment']['snippet']
        comment_data[item_id] = content

    with open('gafford_total_comments.json', 'w') as outfile:
        video_comments = json.dumps(comment_data)
        outfile.write(video_comments)

    comment_data_cleaned = {}

    id_counter = 0

    with open('gafford_total_comments.json', 'r') as f:
        content = json.load(f)
        

        for data in content:
            items = content[data]['items']
            
            for dic in items:
                    
                try:

                    vid_id = dic['snippet']['topLevelComment']['snippet']['videoId']
                    comm = dic['snippet']['topLevelComment']['snippet']['textOriginal']
                    viewerRating = dic['snippet']['topLevelComment']['snippet']['viewerRating']
                    likeCount = dic['snippet']['topLevelComment']['snippet']['likeCount']
                    date = dic['snippet']['topLevelComment']['snippet']['publishedAt']

                    comment_data_cleaned[id_counter] = {}
                    comment_data_cleaned[id_counter]['video_id'] = vid_id
                    comment_data_cleaned[id_counter]['comment'] = comm
                    comment_data_cleaned[id_counter]['viewerRating'] = viewerRating
                    comment_data_cleaned[id_counter]['likeCount'] = likeCount
                    comment_data_cleaned[id_counter]['date'] = date

                    pprint(comment_data_cleaned[id_counter])

                    id_counter += 1

                    try:
                        replies = dic['replies']['comments']

                        for reply in replies:
                            vid_id = reply['snippet']['topLevelComment']['snippet']['videoId']
                            comm = reply['snippet']['topLevelComment']['snippet']['textOriginal']
                            viewerRating = reply['snippet']['topLevelComment']['snippet']['viewerRating']
                            likeCount = reply['snippet']['topLevelComment']['snippet']['likeCount']
                            date = reply['snippet']['topLevelComment']['snippet']['publishedAt']

                            comment_data_cleaned[id_counter] = {}
                            comment_data_cleaned[id_counter]['video_id'] = vid_id
                            comment_data_cleaned[id_counter]['comment'] = comm
                            comment_data_cleaned[id_counter]['viewerRating'] = viewerRating
                            comment_data_cleaned[id_counter]['likeCount'] = likeCount
                            comment_data_cleaned[id_counter]['date'] = date

                            pprint(comment_data_cleaned[id_counter])
                            id_counter += 1

                    except:
                        continue
                except:
                    continue
                    print('skipped')
            
            
    pprint(comment_data_cleaned)
    '''
    with open('gafford_total_comments_cleaned.json', 'w') as outfile:
        video_comments = json.dumps(comment_data_cleaned)
        outfile.write(video_comments)
    '''
    
    if os.path.exists('gafford_total_comments_cleaned.json'):
        write_method = 'a'
        print('Appended JSON file')
    else:
        write_method = 'w'
        print('Created new JSON file')
    
    outfile = open('gafford_total_comments_cleaned.json', write_method)
    outfile.write(json.dumps(comment_data_cleaned))
    outfile.close()

