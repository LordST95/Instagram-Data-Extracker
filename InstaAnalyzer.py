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

conn.execute('''CREATE TABLE InstaUser
         (pk INT PRIMARY KEY     NOT NULL,
         is_follower           INTEGER,
         is_following            INTEGER,
         is_private            INTEGER,
         is_verified            INTEGER,
         liked_images            TEXT,
         username        TEXT,
         full_name        TEXT,
         UNIQUE(pk)
         );''')


print("Working on followers")
rank_token = api.generate_uuid(return_hex=False, seed=None)
result = api.user_followers(userID, rank_token)
users = result.get('users', [])
for x in users:
    user_name = x.get('username', []).encode('utf-8')
    full_name = x.get('full_name', []).encode('utf-8')
    pk = x.get('pk', [])
    is_verified =  '1' if x.get('is_verified', []) else '0'
    is_private = '1' if x.get('is_private', []) else '0'
    params = (pk, 1, 0, is_private, is_verified, '', user_name, full_name)
    conn.execute("insert into InstaUser values (?, ?, ?, ?, ?, ?, ?, ?)", params)
big_list=result.get('big_list', [])
while big_list:
    result = api.user_followers(userID, rank_token, max_id = result.get('next_max_id', []))
    big_list=result.get('big_list', [])
    users = result.get('users', [])
    for x in users:
        user_name = x.get('username', []).encode('utf-8')
        full_name = x.get('full_name', []).encode('utf-8')
        pk = x.get('pk', [])
        is_verified =  '1' if x.get('is_verified', []) else '0'
        is_private = '1' if x.get('is_private', []) else '0'
        params = (pk, 1, 0, is_private, is_verified, '', user_name, full_name)
        conn.execute("insert into InstaUser values (?, ?, ?, ?, ?, ?, ?, ?)", params)


print("Working on following")
result = api.user_following(userID, rank_token)
users = result.get('users', [])
for x in users:
    pk = x.get('pk', [])
    conn.execute("UPDATE InstaUser set is_following = 1 where pk = "+str(pk))
    conn.commit
    user_name = x.get('username', []).encode('utf-8')
    full_name = x.get('full_name', []).encode('utf-8')
    is_verified =  '1' if x.get('is_verified', []) else '0'
    is_private = '1' if x.get('is_private', []) else '0'
    params = (pk, 0, 1, is_private, is_verified, '', user_name, full_name)
    conn.execute("INSERT OR IGNORE INTO InstaUser VALUES (?, ?, ?, ?, ?, ?, ?, ?)", params)
big_list=result.get('big_list', [])
while big_list:
    result = api.user_following(userID, rank_token, max_id = result.get('next_max_id', []))
    big_list=result.get('big_list', [])
    users = result.get('users', [])
    for x in users:
        pk = x.get('pk', [])
        conn.execute("UPDATE InstaUser set is_following = 1 where pk = "+str(pk))
        conn.commit
        user_name = x.get('username', []).encode('utf-8')
        full_name = x.get('full_name', []).encode('utf-8')
        is_verified =  '1' if x.get('is_verified', []) else '0'
        is_private = '1' if x.get('is_private', []) else '0'
        params = (pk, 0, 1, is_private, is_verified, '', user_name, full_name)
        conn.execute("INSERT OR IGNORE INTO InstaUser VALUES (?, ?, ?, ?, ?, ?, ?, ?)", params)


print("Working on your medias")
result = api.user_detail_info(userID).get('feed', [])
items = result.get('items', [])
counter = 1
for x in items:
    media_id = x.get('pk', [])
    like_count = str(x.get('like_count', []))
    comment_count = str(x.get('comment_count', []))
    print("Working on media NO "+str(counter)+" ==> "+str(media_id))
    counter = counter + 1

    for x in api.media_likers(media_id).get('users', []):
        pk = x.get('pk', [])
        liked_images = ''
        cursor = conn.execute("SELECT liked_images from InstaUser where pk = "+str(pk))
        for row in cursor:
           liked_images=str(row[0])+"|("+str(media_id)+","+like_count+","+comment_count+")"

        conn.execute("UPDATE InstaUser set liked_images = ? where pk = ?", (liked_images, pk))
        conn.commit
more_available=result.get('more_available', [])
while more_available:
    result = api.user_detail_info(userID, max_id=result.get('next_max_id', [])).get('feed', [])
    more_available=result.get('more_available', [])
    items = result.get('items', [])
    for x in items:
        media_id = x.get('pk', [])
        like_count = str(x.get('like_count', []))
        comment_count = str(x.get('comment_count', []))
        print("Working on media NO "+str(counter)+" ==> "+str(media_id))
        counter = counter + 1

        for x in api.media_likers(media_id).get('users', []):
            pk = x.get('pk', [])
            liked_images = ''
            cursor = conn.execute("SELECT liked_images from InstaUser where pk = "+str(pk))
            for row in cursor:
                liked_images=str(row[0])+"|("+str(media_id)+","+like_count+","+comment_count+")"

            conn.execute("UPDATE InstaUser set liked_images = ? where pk = ?", (liked_images, pk))
            conn.commit



print("Wrting your data to CSV files")
with open('InstaInfo.csv', 'w') as csvfile:
    fieldnames = ['pk', 'is_follower', 'is_following', 'is_private', 'is_verified', 'liked_images', 'username', 'full_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    cursor = conn.execute("SELECT * from InstaUser")
    for row in cursor:
        writer.writerow(
            {
                'pk': row[0],
                'is_follower': row[1],
                'is_following': row[2],
                'is_private': row[3],
                'is_verified': row[4],
                'liked_images': row[5],
                'username': row[6],
                'full_name': row[7]
            }
        )


conn.close()
