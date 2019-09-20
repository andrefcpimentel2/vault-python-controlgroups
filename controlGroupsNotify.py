import re
import hvac
import json
import requests
import os
import sys
from optparse import OptionParser
from requests.auth import HTTPBasicAuth

VAULT_ADDRESS =  os.environ.get('VAULT_ADDR', None)
VAULT_TOKEN =  os.environ.get('VAULT_TOKEN', None)

namespace = ""

# if namespace:
#     namespace+"/"

client = hvac.Client(
    url=VAULT_ADDRESS,
    token=VAULT_TOKEN
    )


def readTokenAccessor():
    headers = {"X-Vault-Token": VAULT_TOKEN}
    request_url = VAULT_ADDRESS+"/v1/"+namespace+"auth/token/accessors"
    response = requests.request("LIST", request_url, headers=headers)
    paths = list()

    if(response.ok):

        jData = json.loads(response.content)
        for tokenAccessor in jData['data']['keys']:
            search_result = searchForPolicy(tokenAccessor)
            if search_result:
                paths.append(search_result)
    else:
        response.raise_for_status()

    return paths

def searchForPolicy(tokenAccessor):
    headers = {"X-Vault-Token": VAULT_TOKEN}
    payload = {"accessor": tokenAccessor}
    request_url = VAULT_ADDRESS+"/v1/"+namespace+"auth/token/lookup-accessor"
    response = requests.post( request_url, headers=headers, json=payload)

    if(response.ok):

        jData = json.loads(response.content)

        if "control-group"in jData['data']['policies']:
            return getRequestInfo(jData['data']['accessor'])
    else:
        response.raise_for_status()

    return None

def getRequestInfo(accessor):
    headers = {"X-Vault-Token": VAULT_TOKEN}
    payload = {"accessor": accessor }
    request_url = VAULT_ADDRESS+"/v1/"+namespace+"sys/control-group/request"
    response = requests.post( request_url, headers=headers, json=payload)

    if(response.ok):

        jData = json.loads(response.content)
        if not jData['data']['approved']:
            return {
               'path': jData['data']['request_path'],
               'entity': jData['data']['request_entity'].get('name', "Name not found"),
               'accessor': accessor
            }
    else:
        response.raise_for_status()

    return None


#Main gets list of entities and creates groups/policies/kv for each entity
def main():
    readTokenAccessor()


if __name__ == '__main__':
    main()