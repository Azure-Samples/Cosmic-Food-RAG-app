targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string
@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('SKU to use for App Service Plan')
param appServiceSku string

var mongoClusterName = '${uniqueString(resourceGroup.id)}-mvcore'
var mongoAdminUser = 'admin${uniqueString(resourceGroup.id)}'
@secure()
@description('Mongo Server administrator password')
param mongoAdminPassword string

@description('SKU to use for Cosmos DB for MongoDB vCore Plan')
param mongoServiceSku string

// https://learn.microsoft.com/azure/ai-services/openai/concepts/models?tabs=python-secure%2Cstandard%2Cstandard-chat-completions#standard-deployment-model-availability
@description('Location for the OpenAI resource group')
@allowed([
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'switzerlandnorth'
  'uksouth'
  'japaneast'
  'northcentralus'
  'australiaeast'
  'swedencentral'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAiLocation string
param openAIDeploymentName string = '${name}-openai'
param chatGptDeploymentName string = 'gpt-4o'
param chatGptDeploymentCapacity int = 8
param chatGptModelName string = 'gpt-4o'
param chatGptModelVersion string = '2024-11-20'
param embeddingDeploymentName string = 'text-embedding-ada-002'
param embeddingDeploymentCapacity int = 30
param embeddingModelName string = 'text-embedding-ada-002'

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var tags = { 'azd-env-name': name }
var prefix = '${name}-${resourceToken}'
var rgName = '${prefix}-rg'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: rgName
  location: location
  tags: tags
}

// Store secrets in a keyvault
module keyVault './core/security/keyvault.bicep' = {
  name: 'keyvault'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 17)}-vault'
    location: location
    tags: tags
    principalId: principalId
  }
}

var openAiDeployments = [
  {
    name: chatGptDeploymentName
    model: {
      format: 'OpenAI'
      name: chatGptModelName
      version: chatGptModelVersion
    }
    sku: {
      name: 'Standard'
      capacity: chatGptDeploymentCapacity
    }
  }
  {
    name: embeddingDeploymentName
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: '2'
    }
    sku: {
      name: 'Standard'
      capacity: embeddingDeploymentCapacity
    }
  }
]

module openAi 'core/ai/cognitiveservices.bicep' = {
  name: 'openai'
  scope: resourceGroup
  params: {
    name: openAIDeploymentName
    location: openAiLocation
    tags: tags
    sku: {
      name: 'S0'
    }
    deployments: openAiDeployments
  }
}

module cognitiveServiceSecret './app/key-vault-secrets.bicep' = {
  name: 'keyvaultsecret-cognitiveservice'
  scope: resourceGroup
  params: {
    rgName: rgName
    keyVaultName: keyVault.outputs.name
    name: 'cognitiveServiceKey'
    cognitiveServiceName: openAi.outputs.name
  }
}

module appServicePlan 'core/host/appserviceplan.bicep' = {
  name: 'serviceplan'
  scope: resourceGroup
  params: {
    name: '${prefix}-serviceplan'
    location: location
    tags: tags
    sku: {
      name: appServiceSku
    }
    reserved: true
  }
}

module mongoCluster 'core/database/cosmos/mongo/cosmos-mongo-cluster.bicep' = {
  name: 'mongoCluster'
  scope: resourceGroup
  params: {
    name: mongoClusterName
    location: location
    tags: tags
    administratorLogin: mongoAdminUser
    administratorLoginPassword: mongoAdminPassword
    storage: 32
    nodeCount: 1
    sku: mongoServiceSku
    allowAzureIPsFirewall: true
  }
}

module keyVaultSecrets './core/security/keyvault-secret.bicep' = {
  dependsOn: [ mongoCluster ]
  name: 'keyvault-secret-mongo-password'
  scope: resourceGroup
  params: {
    name: 'mongoAdminPassword'
    keyVaultName: keyVault.outputs.name
    secretValue: mongoAdminPassword
  }
}

module web 'core/host/appservice.bicep' = {
  name: 'appservice'
  scope: resourceGroup
  params: {
    name: '${prefix}-appservice'
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    appServicePlanId: appServicePlan.outputs.id
    appCommandLine: 'entrypoint.sh'
    runtimeName: 'python'
    runtimeVersion: '3.12'
    scmDoBuildDuringDeployment: true
    ftpsState: 'Disabled'
    managedIdentity: true
    use32BitWorkerProcess: appServiceSku == 'F1'
    alwaysOn: appServiceSku != 'F1'
    appSettings: {
      AZURE_OPENAI_DEPLOYMENT_NAME: openAIDeploymentName
      AZURE_OPENAI_ENDPOINT: openAi.outputs.endpoint
      AZURE_OPENAI_CHAT_MODEL_NAME: chatGptModelName
      AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: chatGptDeploymentName
      AZURE_OPENAI_EMBEDDINGS_MODEL_NAME: embeddingModelName
      AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME: embeddingDeploymentName
      AZURE_OPENAI_API_KEY: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=cognitiveServiceKey)'
      AZURE_COSMOS_PASSWORD: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=mongoAdminPassword)'
      AZURE_COSMOS_CONNECTION_STRING: mongoCluster.outputs.connectionStringKey
      AZURE_COSMOS_USERNAME: mongoAdminUser
      AZURE_COSMOS_DATABASE_NAME: 'CosmicDB'
      AZURE_COSMOS_COLLECTION_NAME: 'CosmicFoodCollection'
      AZURE_COSMOS_INDEX_NAME: 'CosmicIndex'
    }
  }
}

module webKeyVaultAccess 'core/security/keyvault-access.bicep' = {
  name: 'web-keyvault-access'
  scope: resourceGroup
  params: {
    keyVaultName: keyVault.outputs.name
    principalId: web.outputs.identityPrincipalId
  }
}

output WEB_URI string = web.outputs.uri
output AZURE_LOCATION string = location
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
