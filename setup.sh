#! /bin/bash
vault auth enable ldap || true

vault write auth/ldap/config \
    url="ldap://ldap-service.service.consul" \
    binddn="cn=admin,dc=example,dc=org" \
    userattr="uid" \
    bindpass='admin' \
    userdn="ou=Users,dc=example,dc=org" \
    groupdn="ou=Groups,dc=example,dc=org" \
    insecure_tls=true

vault write identity/group name="approvers" \
      policies="superuser" \
      type="external"

vault read identity/group/name/approvers  -format=json | jq -r .data.id > approvers_group_id.txt
vault auth list -format=json  | jq -r '.["ldap/"].accessor' > accessor.txt

vault write identity/group-alias name="approvers" \
        mount_accessor=$(cat accessor.txt) \
        canonical_id=$(cat approvers_group_id.txt)


vault kv put kv/cgtest example=value
