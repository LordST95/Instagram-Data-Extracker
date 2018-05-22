import sqlite3
import csv

from instagram_private_api import Client, ClientCompatPatch

user_name = ''
password = ''

print("connecting to server")
api = Client(user_name, password)
userID = api.authenticated_user_id


conn = sqlite3.connect(":memory:")
# conn = sqlite3.connect('test.db')
conn.text_factory = str

conn.execute('''CREATE TABLE YourActions
         (pk INT PRIMARY KEY     NOT NULL,
         username           TEXT,
         full_name           TEXT,
         is_following           INTEGER,
         Number_of_Liked_Posts           INTEGER,
         UNIQUE(pk)
         );''')


result = api.feed_liked()
items = result.get('items', [])
counter = 1
for x in items:
    media_id = x.get('pk', [])
    like_count = str(x.get('like_count', []))
    comment_count = str(x.get('comment_count', []))
    post_sender = x.get('user', [])
    sender_username = post_sender.get('username', [])
    sender_full_name = post_sender.get('full_name', [])
    sender_pk = post_sender.get('pk', [])
    friendship_status_with_sender = post_sender.get('friendship_status', [])
    do_u_follow_sender = '1' if friendship_status_with_sender.get('following', []) else '0'
    is_bestie = friendship_status_with_sender.get('is_bestie', [])
    print("Working on media NO "+str(counter)+" ==> "+str(media_id))
    counter = counter + 1

    Number_of_Liked_Posts = 0
    cursor = conn.execute("SELECT Number_of_Liked_Posts from YourActions where pk = "+str(sender_pk))
    for row in cursor:
        Number_of_Liked_Posts = str(int(row[0]) + 1)

    # if data ii az taraf too db nabashe chizi update Nmishe
    conn.execute("UPDATE YourActions set Number_of_Liked_Posts = ? where pk = ?", (Number_of_Liked_Posts, sender_pk))
    conn.commit
    params = (sender_pk, sender_username, sender_full_name, do_u_follow_sender, 1)
    # if data ii not exist then we insert it, if it was then we ignore :))
    conn.execute("INSERT OR IGNORE INTO YourActions VALUES (?, ?, ?, ?, ?)", params)

# Testing the reslut :)
# cursor = conn.execute("SELECT username , Number_of_Liked_Posts from YourActions")
# # print(len(cursor.fetchall()))
# for row in cursor:
#        print (row)


more_available=result.get('more_available', [])
while more_available:
    result = api.feed_liked(max_id=result.get('next_max_id', []))
    more_available=result.get('more_available', [])
    items = result.get('items', [])
    for x in items:
        media_id = x.get('pk', [])
        post_sender = x.get('user', [])
        sender_username = post_sender.get('username', [])
        sender_full_name = post_sender.get('full_name', [])
        sender_pk = post_sender.get('pk', [])
        print("Working on media NO "+str(counter)+" ==> "+str(media_id))
        counter = counter + 1

        # Extracting Previous Data
        Number_of_Liked_Posts = 0
        cursor = conn.execute("SELECT Number_of_Liked_Posts from YourActions where pk = "+str(sender_pk))
        for row in cursor:
            Number_of_Liked_Posts = str(int(row[0]) + 1)

        # Insert Or Update the table
        conn.execute("UPDATE YourActions set Number_of_Liked_Posts = ? where pk = ?", (Number_of_Liked_Posts, sender_pk))
        conn.commit
        params = (sender_pk, sender_username, sender_full_name, do_u_follow_sender, 1)
        conn.execute("INSERT OR IGNORE INTO YourActions VALUES (?, ?, ?, ?, ?)", params)




print("Wrting your data to CSV files")
with open('YourActivity.csv', 'w') as csvfile:
    fieldnames = ['pk', 'username', 'full_name', 'is_following', 'Number_of_Liked_Posts']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    cursor = conn.execute("SELECT * from YourActions")
    for row in cursor:
        writer.writerow(
            {
                'pk': row[0],
                'username': row[1],
                'full_name': row[2],
                'is_following': row[3],
                'Number_of_Liked_Posts': row[4]
            }
        )


conn.close()
