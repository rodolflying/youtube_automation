from googleapiclient.discovery import build
import pandas as pd
from time import sleep
import traceback
import os
from dotenv import load_dotenv

# pip install virtualenv
# virtualenv <your-env>
# <your-env>\Scripts\activate
# <your-env>\Scripts\pip.exe install google-api-python-client
load_dotenv()

def get_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        videoId=video_id,
        textFormat="plainText"
    )

    df = pd.DataFrame(columns=['comment', 'replies', 'date', 'user_name'])

    while request:
        replies = []
        comments = []
        dates = []
        user_names = []

        try:
            response = request.execute()

            for item in response['items']:
                # Extracting comments
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)

                user_name = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                user_names.append(user_name)

                date = item['snippet']['topLevelComment']['snippet']['publishedAt']
                dates.append(date)

                # counting number of reply of comment
                replycount = item['snippet']['totalReplyCount']

                # if reply is there
                if replycount > 0:
                    # append empty list to replies
                    replies.append([])
                    # iterate through all reply
                    for reply in item['replies']['comments']:
                        # Extract reply
                        reply = reply['snippet']['textDisplay']
                        # append reply to last element of replies
                        replies[-1].append(reply)
                else:
                    replies.append([])

            # create new dataframe
            df2 = pd.DataFrame({"comment": comments, "replies": replies, "user_name": user_names, "date": dates})
            df = pd.concat([df, df2], ignore_index=True)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
            sleep(2)
            request = youtube.commentThreads().list_next(request, response)
            print("Iterating through next page")
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
            print("Sleeping for 10 seconds")
            sleep(10)
            df.to_csv(f"{video_id}_user_comments.csv", index=False, encoding='utf-8')
            break

def main():
    api_key = os.getenv("API_KEY")
    #You have to extract the video id from the youtube url
    video_id = "tybOi4hjZFQ"
    get_comments(api_key, video_id)

if __name__ == "__main__":
    main()