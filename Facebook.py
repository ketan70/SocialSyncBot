import facebook
import requests
import json 

def get_page_credentials(company_name, page_name):
    with open("credentials.json", "r") as f:
        data = json.load(f)

    for company in data["companies"]:
        if company["company_name"] == company_name:
            for page in company["pages"]:
                if page["page_name"] == page_name:
                    return page["page_id"], page["access_token"]
            break
    return None, None

page_id, access_token = get_page_credentials("raisebe","Facebook")
print(page_id,access_token)


def post_text_status(company_name,page_name, status_message):
    page_id, access_token = get_page_credentials(company_name,page_name)
    
    if page_id and access_token:
        print(page_id,access_token)
        graph = facebook.GraphAPI(access_token=access_token, version="3.0")
        graph.put_object(parent_object=page_id, connection_name='feed', message=status_message)
        posts = graph.get_connections(id=page_id, connection_name="posts", limit=1)
        print("Text status posted successfully.")
        print(posts['data'][0]['id'])
        return posts['data'][0]['id']
    else:
        print("Page not found or credentials not available.")

def post_photo(company_name ,page_name, photo_path, caption=None):
    page_id, access_token = get_page_credentials(company_name ,page_name)

    if page_id and access_token:
        graph = facebook.GraphAPI(access_token=access_token, version="3.0")
        with open(photo_path, "rb") as photo:
            graph.put_photo(parent_object=page_id, image=photo, message=caption)
            posts = graph.get_connections(id=page_id, connection_name="posts", limit=1)
            print("Photo posted successfully.")
            print(posts['data'][0]['id'])
            return posts['data'][0]['id']
    else:
        print("Page not found or credentials not available.")


def post_link(company_name ,page_name, link_url, link_caption, link_description):
    page_id, access_token = get_page_credentials(company_name ,page_name)
    
    if not page_id or not access_token:
        print("Unable to retrieve credentials. Cannot post link.")
        return
    
    graph = facebook.GraphAPI(access_token=access_token, version="3.0")
    
    message = f"{link_caption}\n{link_description}"

    try:
        graph.put_object(parent_object=page_id, connection_name='feed', link=link_url, message=message)
        posts = graph.get_connections(id=page_id, connection_name="posts", limit=1)
        print("Link posted successfully.")
        print(posts['data'][0]['id'])
        return posts['data'][0]['id']
    except facebook.GraphAPIError as e:
        print(f"Error posting link: {e}")
        return None
    

    import pandas as pd
from datetime import datetime

def runallpost():
    df = pd.read_excel("posts.xlsx")
    
    for index, row in df.iterrows():
        company_name = row['Company Name']
        page_name = row['Page Name']
        post_type = row['Post Type']
        post_status = row['Posted']


        page_id, access_token = get_page_credentials(company_name, page_name)

        
        if post_status != "Posted":
            if not (page_id and access_token):
                print(f"Credentials not found for {company_name} - {page_name}. Skipping post.")
                continue
            

            if post_type == 'Text':
                status_message = row['Status Message']
                post_id = post_text_status(company_name, page_name, status_message)
            elif post_type == 'Photo':
                photo_url = row['Photo URL']
                caption = row['Caption']
                post_id = post_photo(company_name, page_name, photo_url, caption)
            elif post_type == 'Link':
                link_url = row['Link URL']
                link_caption = row['Link Caption']
                link_description = row['Link Description']
                post_id = post_link(company_name, page_name, link_url, link_caption, link_description)
            elif post_type == 'Video':
                print("Function is under construction for Event posts.")
                # Similar to other post types, call the relevant function and get the post_id
                # post_id = post_video(company_name, page_name, video_url, title, description)
                post_id =''
            elif post_type == 'Event':
                print("Function is under construction for Event posts.")
                # Similar to other post types, call the relevant function and get the post_id
                # post_id = create_event(company_name, page_name, event_name, start_time, end_time, event_location, description)
                post_id =''
            else:
                print(f"Unknown post type '{post_type}' for {company_name} - {page_name}. Skipping post.")
                continue
            
            # Record the post_id and status in the DataFrame
            df.at[index, 'Post_ID'] = post_id
            print(post_id)
            df.at[index, 'Posted'] = 'Posted' if post_id else 'Failed'
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.at[index, 'created_time'] = current_time

    df.to_excel("posts.xlsx", index=False)

runallpost()