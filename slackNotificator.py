import ldap
import os
import slack
import json
import ssl

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# https://github.com/slackapi/python-slackclient
######## connect to slack ####################################################
client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'],ssl=ssl_context)
######### initialize connection ###############################################
con = ldap.initialize('ldap://workers-1.eu-andrestack.hashidemos.io:389')
# At this point, we're connected as an anonymous user
# If we want to be associated to an account
# you can log by binding your account details to your connection
con.simple_bind_s("cn=admin,dc=example,dc=org", "admin")
ldap_base = "dc=example,dc=org"


def findApprovalGroupMembers(groupname):
    ########## performing a simple ldap query ####################################
    # query = "(uid=juser)"
    query = "(cn="+groupname+")"
    result = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, query)
    (part1, part2) = result[0]
    approverUid = part2['memberUid'][0].decode('ascii','ignore')
    print(approverUid)
    displayName = findSlackByDisplayName(approverUid)
    return displayName


def findSlackByDisplayName(approverUid):
    query = "(uid="+approverUid+")"
    result = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, query)
    (part1, part2) = result[0]
    displayName = part2['displayName'][0].decode('ascii','ignore')
    return displayName

def sendMessage(displayName,requestor,TokenAccessor):
    response = client.chat_postMessage(
    channel="cgtest",
    blocks=[

        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " New control-groups aproval request \n" +
                "Requestor: "+requestor +"\n" +
                " Approve it running: \n" +
                "vault write sys/control-group/authorize accessor="+TokenAccessor
            },
                "accessory": {
                "type": "image",
                "image_url": "https://i.imgur.com/bebeWay.png",
                "alt_text": "Vault"
            }
        }
    ],
    icon_url= "https://i.imgur.com/bebeWay.png",
    )

def privateMessage(displayName,requestor,TokenAccessor):
    response = client.chat_postMessage(
    channel=displayName,
    blocks=[

        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "New control-groups aproval request\n" +
                "Requestor: "+requestor +"\n" +
                "Approve it running: \n" +
                "vault write sys/control-group/authorize accessor="+TokenAccessor
            },
                "accessory": {
                "type": "image",
                "image_url": "https://i.imgur.com/3LdMUNS.png",
                "alt_text": "Vault"
            }
        }
    ],
    icon_url= "https://i.imgur.com/bebeWay.png",
    link_names=1,
    )

def main():
   displayName = findApprovalGroupMembers("approvers")
   sendMessage(displayName,"tiozinho","8QOdwOcVmy41Gl7y031SuAYi")
  # privateMessage(displayName,"tiozinho","8QOdwOcVmy41Gl7y031SuAYi")
  # test("@Andre","tiozinho","8QOdwOcVmy41Gl7y031SuAYi")

if __name__ == '__main__':
    main()