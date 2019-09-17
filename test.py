import json

import controlGroupsNotify as findRequests
import mapVaultKvPolicy as findApproverGroup
import slackNotificator as messageSlack

policy_map = findApproverGroup.mapKVPoliciesCGs()
requests = findRequests.readTokenAccessor()

for request in requests:

    if policy_map.get(request['path'] , None):
        for approving_groups in policy_map[request['path']]:
            displayName = messageSlack.findApprovalGroupMembers(approving_groups)
            #TODO implement Vault KV store to check if messages have been sent already, Do not send message if last message was sent less than 1 hour or something
            messageSlack.sendMessage(displayName, request['entity'], request['accessor'])

