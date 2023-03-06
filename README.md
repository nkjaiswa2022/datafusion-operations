## Description

   Datafusion operations contains the script which helps in monitoring the internal services of datafusion instance. It helps operations or support team to get timely alerts for any service which is experiencing issues.

## Pre-Req & Dependencies :

	* "project_id" and "region" details should be mentioned in the below file.
    'sampleconfig.ini'
	*  Install the below packages
    pip install google-cloud-monitoring google-cloud-data-fusion google-auth google-auth-transport-requests requests ConfigParser


## Run Monitoring script :

	* Run the python script with following command,

		python <instance_list> <service_list>

		Example: python cdf_service_healthCheck_metric.py [instance1,instance2] [service1,service2,service3]

		Arguments Details :

			< instance_list > : provide the instance list
			< service_list > : provide the service list (e.g. metrics, appfabric etc)

	* If the metric does not exist already then the script will create a new metric and push the service status code(200,404,503 etc) 
    for thi metric in cloud monitoring.

		Custom metric path: Generic Task -> custom -> cdf/{PROJECT_NM}/{INSTANCE_NM}/services/healthCheck

	* it will maintain separate metric for each instance.

		Example:

 		Instance1:
 			cdf/{PROJECT_NM}/instance1/services/healthCheck
     			service1 : 200
     			service2 : 503
     			service3 : 200

 		Instance2:
 			cdf/{PROJECT_NM}/instance2/services/healthCheck
     			service1 : 200
     			service2 : 503
     			service3 : 200




  
 
