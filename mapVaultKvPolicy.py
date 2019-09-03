import re
import hvac
import json
import requests
import os
import sys
import hcl
from optparse import OptionParser
from requests.auth import HTTPBasicAuth

# VAULT_ADDRESS =  os.environ.get('VAULT_ADDR', None)
# VAULT_TOKEN =  os.environ.get('VAULT_TOKEN', None)


namespace = ""


   
if namespace:
    namespace+"/"   


client = hvac.Client(
    url=VAULT_ADDRESS,
    token=VAULT_TOKEN,
    #verify=False,
    )

def update(d1,d2):
    c = d1.copy()
    for key in d2:
        if key in d1:c[key].update(d2[key])
        else:c[key] = d2[key]
    return c

def mapKVPoliciesCGs():
 policyList = listPolicies()
 policyMap = {}
 for policy in policyList:
     data = getKVGroupMapping(policy)
     policyMap = update(policyMap, data)
 print (policyMap)


def listPolicies():
    list_policies_resp = client.sys.list_policies()['data']['policies']
    return list_policies_resp

def getKVGroupMapping(policy):
    hvac_policy_rules = client.sys.read_policy(name=policy)['data']['rules']
    data = {}
    # print('secret-writer policy rules:\n%s' % hvac_policy_rules)
    try:
        obj = hcl.loads(hvac_policy_rules)
        # print(json.dumps(obj,indent=4))
        for path in obj['path']:
            # print(json.dumps(obj['path'][path],indent=4)) 
            if "control_group" in obj['path'][path]:
                # print(path) 
                # if not path in data.keys():
                data[path] = []
                # print(path)
                factors = obj['path'][path]['control_group']['factor']                

                 
                # print(json.dumps(obj['path'][path]['control_group']['factor'],indent=4))
                # print(json.dumps(factors,indent=4))

                if type(factors) is dict:
                    for factor in factors :
                        # print(json.dumps(obj['path'][path]['control_group']['factor'][factor]['identity']['group_names'],indent=4))
                        # print(json.dumps(factor)

                        data[path] += factors[factor]['identity']['group_names']

                if type(factors) is list:
                    for factor in factors :
                        for item in factor:
                            data[path] += factor[item]['identity']['group_names']

                data[path] = set (data[path])
                            

                
    except:
        pass
    return data


def main():
    mapKVPoliciesCGs()
    #getApproverGroupEntities(management_group)

if __name__ == '__main__':
    main()