import re
import hvac
import json
import requests
import os
import sys
from optparse import OptionParser
from requests.auth import HTTPBasicAuth

# VAULT_ADDRESS =  os.environ.get('VAULT_ADDR', None)
# VAULT_TOKEN =  os.environ.get('VAULT_TOKEN', None)

management_group = "managers"
namespace = ""


   
if namespace:
    namespace+"/"   

client = hvac.Client(
    url=VAULT_ADDRESS,
    token=VAULT_TOKEN,
    #verify=False,
    )


def readTokenAccessor():
    headers = {"X-Vault-Token": VAULT_TOKEN}
    #payload =
    request_url = VAULT_ADDRESS+"/v1/"+namespace+"auth/token/accessors"
    response = requests.request("LIST", request_url, headers=headers)


    if(response.ok):

        jData = json.loads(response.content)
        for tokenAccessor in jData['data']['keys']:
            searchForPolicy(tokenAccessor)

        # print("The response contains {0} properties".format(len(jData)))
        # print("\n")
        
        # print(json.dumps(jData,indent=2))
    else:
        response.raise_for_status()


def searchForPolicy(tokenAccessor):
    headers = {"X-Vault-Token": VAULT_TOKEN}
    payload = {"accessor": tokenAccessor}
    request_url = VAULT_ADDRESS+"/v1/"+namespace+"auth/token/lookup-accessor"
    response = requests.post( request_url, headers=headers, json=payload)

    if(response.ok):

        jData = json.loads(response.content)

        if "control-group"in jData['data']['policies']:
            getRequestInfo(jData['data']['accessor'])
    else:
        response.raise_for_status()

def getRequestInfo(acessor):
    headers = {"X-Vault-Token": VAULT_TOKEN}
    payload = {"accessor": acessor}
    request_url = VAULT_ADDRESS+"/v1/"+namespace+"sys/control-group/request"
    response = requests.post( request_url, headers=headers, json=payload)

    if(response.ok):

        jData = json.loads(response.content)
        if not jData['data']['approved']:
            print(json.dumps(jData,indent=2))
            #getEntitybyID(jData['data']['request_entity']['id'], jData['data']['request_path'])
            

    else:
        response.raise_for_status()

def getApproverGroupEntities(management_group):

    lookup_response = client.secrets.identity.read_group_by_name(
        name=management_group,
    )
    print(json.dumps(lookup_response,indent=2))
    for entityID in lookup_response['data']['member_entity_ids']:
        getEntityAlias(entityID)

     
def getEntityAlias(entityID):

    read_response = client.secrets.identity.read_entity(
            entity_id=entityID,
    )

    if read_response['data']['aliases'][0]['mount_type'] == "oidc":
        name = read_response['data']['aliases'][0]['metadata']['name']
        email = read_response['data']['aliases'][0]['metadata']['email']
    elif read_response['data']['aliases'][0]['mount_type'] == "github":
        name = read_response['data']['aliases'][0]['name']
        email = findEmailFromGitHubUsername(name)
    
    print('Name for entity ID {id} is: {name}'.format(id=entityID, name=name))
    return name

def findEmailFromGitHubUsername(username):

    gh_api_url = 'https://api.github.com/users/{username}/events/public'

    r = requests.get(gh_api_url)
    r.raise_for_status()

    gh_public_events = r.json()

    if isinstance(gh_public_events, dict):
        if gh_public_events.get('message') and gh_public_events.get('message') == 'Not Found':
            print('User was not found!')
            sys.exit(0)

    fullname = 'N/A'
    email = 'N/A'

    for event in gh_public_events:
        if event.get('payload').get('commits'):
            commits = event.get('payload').get('commits')
            for commit in commits:
                if commit.get('author'):
                    fullname = commit.get('author').get('name')
                    email = commit.get('author').get('email')
                    break

    print('Full Name: {name}'.format(name=fullname))
    print('email: {email}'.format(email=email))
    return email


# def getEntitybyID(EntityId, request_path):

#     response = client.secrets.identity.read_entity(
#         entity_id=EntityId,
# )
   # print(json.dumps(response,indent=2))


#Main gets list of entities and creates groups/policies/kv for each entity
def main():
    print("Foo")
    readTokenAccessor()
    getApproverGroupEntities(management_group)

if __name__ == '__main__':
    main()