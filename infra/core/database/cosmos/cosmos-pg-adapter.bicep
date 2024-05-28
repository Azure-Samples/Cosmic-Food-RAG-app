param name string
param location string = resourceGroup().location
param tags object = {}

param administratorLogin string
@secure()
param administratorLoginPassword string

param coordinatorServerEdition string
param coordinatorStorageQuotainMb int
param coordinatorVCores int
param databaseName string
param nodeCount int
param nodeVCores int
param allowAzureIPsFirewall bool = false
param allowAllIPsFirewall bool = false
param allowedSingleIPs array = []
param postgresqlVersion string

resource postgresCluster 'Microsoft.DBforPostgreSQL/serverGroupsv2@2023-03-02-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    coordinatorServerEdition: coordinatorServerEdition
    coordinatorStorageQuotaInMb: coordinatorStorageQuotainMb
    coordinatorVCores: coordinatorVCores
    postgresqlVersion: postgresqlVersion
    nodeCount: nodeCount
    nodeVCores: nodeVCores
    databaseName: databaseName
  }

  resource firewall_all 'firewallRules' = if (allowAllIPsFirewall) {
    name: 'allow-all-IPs'
    properties: {
      startIpAddress: '0.0.0.0'
      endIpAddress: '255.255.255.255'
    }
  }

  resource firewall_azure 'firewallRules' = if (allowAzureIPsFirewall) {
    name: 'allow-all-azure-internal-IPs'
    properties: {
      startIpAddress: '0.0.0.0'
      endIpAddress: '0.0.0.0'
    }
  }

  resource firewall_single 'firewallRules' = [for ip in allowedSingleIPs: {
    name: 'allow-single-${replace(ip, '.', '')}'
    properties: {
      startIpAddress: ip
      endIpAddress: ip
    }
  }]

}

output domainName string = postgresCluster.properties.serverNames[0].fullyQualifiedDomainName
