import requests
import base64
import time
import os
import json
import csv


TOKEN = "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"
URL_FILE_PATH = r'C:\Users\ajhot\Documents\Maslow\abundance_files\urls.txt'
CSV_FILE_PATH = 'atom_connections.csv'


# Download from repo
def download_file_from_github(owner, repo, filepath):
    time.sleep(0.5)

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
    
    headers = {}
    headers['Authorization'] = f'token {TOKEN}'
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content_data = response.json()
        file_content = base64.b64decode(content_data['content']).decode('utf-8')
        json_data = json.loads(file_content) 
        return json_data
    else:
        raise Exception(f"Failed to fetch file. HTTP Status Code: {response.status_code}")


def read_and_morph_urls(file_path):
    urls = [] 

    with open(file_path, 'r') as file:
        for line in file:
            original_url = line.strip()

            if original_url.startswith("https://github.com/"):
                # Extract the owner and repo name from the URL
                parts = original_url.replace("https://github.com/", "").split("/")
                if len(parts) >= 2:
                    owner = parts[0]
                    repo = parts[1]
                    morphed_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
                    urls.append(morphed_url)

    return urls



def process_urls(urls):
    failed_urls = []  

    headers = {'Authorization': f'token {TOKEN}'}

    for url in urls:
        first_url_attempt = url + "/project.maslowcreate"
        
        try:
            # Try to download from the maslowcreate URL
            response = requests.get(first_url_attempt, headers=headers)
            if response.status_code == 200:
                print(f"Successfully downloaded from: {first_url_attempt}")
                content_data = response.json()
                file_content = base64.b64decode(content_data['content']).decode('utf-8')
                json_data = json.loads(file_content) 
                connections = extract_connections(json_data)
                write_connections_to_csv(connections, CSV_FILE_PATH)
                continue
            else:
                raise Exception(f"Failed to fetch file from {first_url_attempt}, status code: {response.status_code}")
        
        except Exception as e:
            print(e)
            # Try to download from the project.abundance URL
            second_url_attempt = url + "/project.abundance"
            
            try:
                response = requests.get(second_url_attempt, headers=headers)
                if response.status_code == 200:
                    print(f"Successfully downloaded from: {second_url_attempt}")
                    content_data = response.json()
                    file_content = base64.b64decode(content_data['content']).decode('utf-8')
                    json_data = json.loads(file_content)  
                    connections = extract_connections(json_data)
                    write_connections_to_csv(connections, CSV_FILE_PATH)
                    continue  
                else:
                    raise Exception(f"Failed to fetch file from {second_url_attempt}, status code: {response.status_code}")
            
            except Exception as e:
                print(e)
                failed_urls.append(url)

    print("\nFailed URLs:")
    for failed_url in failed_urls:
        print(failed_url)



def extract_connections(data):
    connections = []
    atom_id_map = {}

    def build_atom_id_map(atoms):
        try:
            for atom in atoms:
                if 'uniqueID' in atom:
                    atom_id_map[atom['uniqueID']] = atom['atomType']
                    if atom['atomType'] == 'Molecule' and 'allAtoms' in atom:
                        build_atom_id_map(atom['allAtoms'])
        except Exception as e:
            print(f"Error while building atom ID map: {e}")

    def find_connections(connection_list):
        try:
            for connection in connection_list:
                try:
                    if "ap1ID" in connection and "ap2ID" in connection:
                        a1 = connection["ap1ID"]
                        a2 = connection["ap2ID"] 
                        if a1 in atom_id_map and a2 in atom_id_map:
                            connection = (f"{atom_id_map[a1]}", f"{atom_id_map[a2]}")
                            connections.append(connection)
                except KeyError as e:
                    print(f"Missing key in atom data: {e}")
                except Exception as e:
                    print(f"Error while processing ioValues for atom {connection.get('name', 'unknown')}: {e}")

        except Exception as e:
            print(f"Error while finding connections: {e}")

    try:
        if 'allAtoms' in data:
            build_atom_id_map(data['allAtoms']) 
        elif 'molecules' in data and isinstance(data['molecules'], list):
            for molecule in data['molecules']: 
                build_atom_id_map(molecule['allAtoms'])
        else:
            print("No valid atoms or molecules found.")
    except Exception as e:
        print(f"Error while building atom ID map at top level: {e}")

    try:
        if 'allConnectors' in data:
            find_connections(data['allConnectors'])  
        elif 'molecules' in data and isinstance(data['molecules'], list):
            for molecule in data['molecules']:  
                find_connections(molecule['allConnectors'])
        else:
            print("No valid connections found.")
    except Exception as e:
        print(f"Error while finding connections at top level: {e}")

    return connections




def write_connections_to_csv(connections, file_path):
    file_exists = os.path.isfile(file_path)

    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Source Atom', 'Target Atom'])
        for connection in connections:
            writer.writerow(connection)


if __name__ == "__main__":
    urls = read_and_morph_urls(URL_FILE_PATH)
    process_urls(urls)


# # Example usage
# try:
#     file_content = download_file_from_github("ajhotrum", "sfasdgd", "project.abundance")
#     pairs = extract_connections(file_content)
#     write_connections_to_csv(pairs, CSV_FILE_PATH)
#     print(f"Connections written to {CSV_FILE_PATH}")

# except Exception as e:
#     print(e)