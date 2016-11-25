# Invoking notifications out of Azure ML Experiments
This simple python script can submit WMS (Windows Messaging Service) toast notifications straight out of a ML Predictive Experiment

# Requirements
1. Azure ML experiment set-up
2. Update connection string to your Azure Notification Hub in the code

Refer to scenario.png for implementation details.

P.S.: supports WMS notifications only, can be extended to support all notification types using the script here: https://github.com/Azure/azure-notificationhubs-samples/blob/master/notificationhubs-rest-python/NotificationHub.py