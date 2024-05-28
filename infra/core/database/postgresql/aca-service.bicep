param name string
param location string = resourceGroup().location
param tags object = {}

param containerAppsEnvironmentId string

resource postgres 'Microsoft.App/containerApps@2023-04-01-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
    environmentId: containerAppsEnvironmentId
    configuration: {
      service: {
          type: 'postgres'
      }
    }
  }
}

/*
resource pgsqlCli 'Microsoft.App/containerApps@2023-04-01-preview' = {
  name: '${name}-cli'
  location: location
  properties: {
    environmentId: containerAppsEnvironmentId
    template: {
      serviceBinds: [
        {
          serviceId: postgres.id
        }
      ]
      containers: [
        {
          name: 'psql'
          image: 'mcr.microsoft.com/k8se/services/postgres:14'
          command: [ '/bin/sleep', 'infinity' ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 1
      }
    }
  }
}
*/

output id string = postgres.id
