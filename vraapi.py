import requests
import json
from prettytable import PrettyTable
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # Disable SSL warning

def vra_auth(vrafqdn, user, password, tenant):
    """
    Builds an authentication token for the user. Takes input of the fqdn of vRA, username,
    password, and tenant
    """
    url = "https://{}/identity/api/tokens".format(vrafqdn)
    payload = '{{"username":"{}","password":"{}","tenant":"{}"}}'.format(user, password, tenant)
    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        }
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    j = response.json()['id']
    auth = "Bearer "+j
    return auth

def return_vra_vms_asTable(vrafqdn, user, password, tenant):
    """
    Builds a table using PrettyTable to return vRA provisioned VM Details
    """
    auth = vra_auth(vrafqdn, user, password, tenant)
    vraheaders = {
        'accept': "application/json",
        'authorization': auth
        }
    vraApiUrl = "https://{}/catalog-service/api/consumer/resources".format(vrafqdn)
    req = requests.request("GET", vraApiUrl, headers=vraheaders, verify=False).json()['content']
    vratable = PrettyTable(['Name', 'ID', 'OS'])
    for i in req:
        if i['resourceTypeRef']['id'] == 'Infrastructure.Virtual':
            resid = i['id']
            vraResUrl = "https://{}/catalog-service/api/consumer/resources/{}".format(vrafqdn, resid)
            resreq = requests.request("GET", vraResUrl, headers=vraheaders, verify=False).json()
            vratable.add_row((i['name'], i['id'], resreq['resourceData']['entries'][0]['value']['value']))
    return print(vratable)


def vra_build(vrafqdn, user, password, tenant, blueprint):
    """
    Provisions a catalog item with the default template. Takes inputs same as above,
    also requires blueprint name in string format.  
    """
    varray = {}
    auth = vra_auth(vrafqdn, user, password, tenant)
    vraApiUrl = "https://{}/catalog-service/api/consumer/entitledCatalogItemViews".format(vrafqdn)
    vraheaders = {
        'accept': "application/json",
        'authorization': auth
        }
    tempres = requests.request("GET", vraApiUrl, headers=vraheaders, verify=False)
    for i in tempres.json()['content']:
        p = i['name']
        q = i['catalogItemId']
        varray[p] = q
    template = "https://{}/catalog-service/api/consumer/entitledCatalogItems/{}/requests/template".format(vrafqdn, varray[blueprint])
    req = "https://{}/catalog-service/api/consumer/entitledCatalogItems/{}/requests".format(vrafqdn, varray[blueprint])
    templateJson = requests.request("GET", template, headers=vraheaders, verify=False)
    vraCatDeploy = requests.request("Post", req, headers=vraheaders, data=templateJson, verify=False)
    buildStatus = "a "+blueprint+" Server build has been requested"
    return buildStatus
