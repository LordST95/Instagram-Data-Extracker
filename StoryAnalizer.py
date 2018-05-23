import sqlite3
import csv

from instagram_private_api import Client, ClientCompatPatch

user_name = ''
password = ''

print("connecting to server")
api = Client(user_name, password)
userID = api.authenticated_user_id

conn = sqlite3.connect(":memory:")
conn.text_factory = str

conn.execute('''CREATE TABLE StoryUser
         (pk INT PRIMARY KEY     NOT NULL,
         username        TEXT,
         seen_stories           TEXT,
         UNIQUE(pk)
         );''')

result = api.user_reel_media(userID)
items = result.get('items', [])
for x in items:
    story_id = x.get('pk', [])
    total_viewer_count = x.get('total_viewer_count', [])

    print("working story "+str(story_id))

    result = api.story_viewers(story_id)
    for x in result.get('users', []):
        username = x.get('username', [])
        user_pk = x.get('pk', [])

        # Extractind seen_stories from DB
        seen_stories = ''
        cursor = conn.execute("SELECT seen_stories from StoryUser where pk = "+str(user_pk))
        for row in cursor:
            seen_stories=str(row[0])+"|("+str(story_id)+","+str(total_viewer_count)+")"

        # if data ii az taraf too db nabashe chizi update Nmishe
        conn.execute("UPDATE StoryUser set seen_stories = ? where pk = ?", (seen_stories, user_pk))
        conn.commit
        params = (user_pk, username, "("+str(story_id)+","+str(total_viewer_count)+")")
        # if data ii not exist then we insert it, if it was then we ignore :))
        conn.execute("INSERT OR IGNORE INTO StoryUser VALUES (?, ?, ?)", params)
    next_max_id = result.get('next_max_id', [])
    while (next_max_id is not None):
        result = api.story_viewers(story_id, max_id= result.get('next_max_id', []))
        next_max_id = result.get('next_max_id', [])
        for x in result.get('users', []):
            username = x.get('username', [])
            user_pk = x.get('pk', [])
            seen_stories = ''
            cursor = conn.execute("SELECT seen_stories from StoryUser where pk = "+str(user_pk))
            for row in cursor:
                seen_stories=str(row[0])+"|("+str(story_id)+","+str(total_viewer_count)+")"
            conn.execute("UPDATE StoryUser set seen_stories = ? where pk = ?", (seen_stories, user_pk))
            conn.commit
            params = (user_pk, username, "("+str(story_id)+","+str(total_viewer_count)+")")
            conn.execute("INSERT OR IGNORE INTO StoryUser VALUES (?, ?, ?)", params)



print("Wrting your data to CSV files")
with open('StoryInfo.csv', 'w') as csvfile:
    fieldnames = ['pk', 'username', 'seen_stories']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    cursor = conn.execute("SELECT * from StoryUser")
    for row in cursor:
        writer.writerow(
            {
                'pk': row[0],
                'username': row[1],
                'seen_stories': row[2]
            }
        )


conn.close()


# Show Results
# cursor = conn.execute("SELECT * from StoryUser")
# for row in cursor:
#     print (row)


