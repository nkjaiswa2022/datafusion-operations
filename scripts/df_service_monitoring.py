# Copyright 2022 Google LLC. This software is provided as is, without warranty 
# or representation for any use or purpose. 
# Your use of it is subject to your agreement with Google.

"""
This script checks the status of data fusion services and publishes the custom metric to cloud monitoring

Example:
    $ python /home/cdf_service_healthCheck_metric.py <instance list> <service list>
    $ python /home/cdf_service_healthCheck_metric.py [instance1,instance2] [appfabric,service,metadata.service,metrics,metrics.processor,runtime,wrangler.service,pipeline.studio]

Prerequisite:
    pip install google-cloud-monitoring google-cloud-data-fusion google-auth requests ConfigParser
""" 

from google.cloud import data_fusion_v1
from google.cloud import monitoring_v3
import google.auth
import google.auth.transport.requests
import requests
import time
from configparser import ConfigParser
import sys


parser = ConfigParser()
parser.read('sampleconfig.ini')
PROJECT_NM = parser.get('gcp','PROJECT_NM')
region = parser.get('gcp','region')
instanceList = sys.argv[1]
INSTANCE_LIST = instanceList.strip('[]').split(',')
serviceList = sys.argv[2]
SERVICE_LIST = serviceList.strip('[]').split(',')

def get_CDAPendpoint(project_id, region, instance_name):
    client = data_fusion_v1.DataFusionClient()
    name = f"projects/{project_id}/locations/{region}/instances/{instance_name}"
    request = data_fusion_v1.GetInstanceRequest(name=name)
    response = client.get_instance(request=request)
    api_endpoint = response.api_endpoint
    return api_endpoint

for INSTANCE_NM in INSTANCE_LIST:
    CDAP_ENDPOINT = get_CDAPendpoint(PROJECT_NM, region, INSTANCE_NM)

    for service_name in SERVICE_LIST:
        credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        #credentials = service_account.Credentials.from_service_account_file('//etc/sa-data-fusion-pipeline-run.json', scopes=['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/userinfo.email'])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        AUTH_TOKEN = credentials.token
        headers = {"Authorization": "Bearer "+AUTH_TOKEN}
        if service_name == "wrangler.service":
            request_url = f"{CDAP_ENDPOINT}/v3/namespaces/system/apps/dataprep/services/service/status"
            response = requests.get(request_url, headers=headers)
            status = response.status_code
        elif service_name == "pipeline.studio":
            request_url = f"{CDAP_ENDPOINT}/v3/namespaces/system/apps/pipeline/services/studio/status"
            response = requests.get(request_url, headers=headers)
            status = response.status_code
        else:
            request_url = f"{CDAP_ENDPOINT}/v3/system/services/{service_name}/status"
            response = requests.get(request_url, headers=headers)
            status = response.status_code
        
        #send service statuscode to cloud monitoring metrics
        client = monitoring_v3.MetricServiceClient()
        project_name = client.common_project_path(PROJECT_NM)
        series = monitoring_v3.types.TimeSeries()

        # Set resource labels
        series.resource.type = 'generic_task'
        series.resource.labels['task_id'] = PROJECT_NM
        series.resource.labels['job'] = INSTANCE_NM
        series.resource.labels['namespace'] = "default"
        series.resource.labels['location'] = region

        # Set metric labels
        series.metric.type = f"custom.googleapis.com/cdf/{PROJECT_NM}/{INSTANCE_NM}/services/healthCheck"
        series.metric.labels['project_id'] = PROJECT_NM
        series.metric.labels['serive_name'] = service_name

        # Set metric value
        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval({"end_time": {"seconds": seconds, "nanos": nanos}})
        point = monitoring_v3.Point({"interval": interval , "value": {"double_value": status}})
        series.points = [point]
        client.create_time_series(request={"name": project_name, "time_series": [series]})


