targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param name string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Whether the deployment is running on GitHub Actions')
param runningOnGh string = ''

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('SKU to use for App Service Plan')
param appServiceSku string

var mongoClusterName = '${uniqueString(resourceGroup.id)}-vcore'
var mongoAdminUser = 'admin${uniqueString(resourceGroup.id)}'
@secure()
@description('Mongo Server administrator password')
param mongoAdminPassword string

@description('SKU to use for Cosmos DB for MongoDB vCore Plan')
param mongoServiceSku string

@description('Location for the MongoDB Cosmos DB resource if not specified, it will use the primary location')
param mongoServiceLocation string = location

// https://learn.microsoft.com/azure/ai-services/openai/concepts/models?tabs=python-secure%2Cstandard%2Cstandard-chat-completions#standard-deployment-model-availability
@minLength(1)
@description('Location for the OpenAI resource')
@allowed([
  'australiaeast'
  'brazilsouth'
  'canadaeast'
  'eastus'
  'eastus2'
  'francecentral'
  'germanywestcentral'
  'japaneast'
  'koreacentral'
  'northcentralus'
  'norwayeast'
  'polandcentral'
  'spaincentral'
  'southafricanorth'
  'southcentralus'
  'southindia'
  'swedencentral'
  'switzerlandnorth'
  'uksouth'
  'westeurope'
  'westus'
  'westus3'
])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAILocation string

@description('Name of the OpenAI resource group. If not specified, the resource group name will be generated.')
param openAIResourceGroupName string = ''

@description('Whether to deploy Azure OpenAI resources')
param deployAzureOpenAI bool = true

@allowed([
  'azure'
  'openaicom'
])
param openAIChatHost string = 'azure'

@allowed([
  'azure'
  'openaicom'
])
param openAIEmbedHost string = 'azure'

@secure()
param openAIComKey string = ''

param azureOpenAIAPIVersion string = '2024-03-01-preview'

@secure()
param azureOpenAIKey string = ''

@description('Azure OpenAI endpoint to use, if not using the one deployed here.')
param azureOpenAIEndpoint string = ''

// Chat completion model
@description('Name of the chat model to deploy')
param chatModelName string // Set in main.parameters.json
@description('Name of the model deployment')
param chatDeploymentName string // Set in main.parameters.json

@description('Version of the chat model to deploy')
// See version availability in this table:
// https://learn.microsoft.com/azure/ai-services/openai/concepts/models#global-standard-model-availability
param chatDeploymentVersion string // Set in main.parameters.json

@description('Sku of the chat deployment')
param chatDeploymentSku string // Set in main.parameters.json

@description('Capacity of the chat deployment')
// You can increase this, but capacity is limited per model/region, so you will get errors if you go over
// https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
param chatDeploymentCapacity int // Set in main.parameters.json

// Embedding model
@description('Name of the embedding model to deploy')
param embedModelName string // Set in main.parameters.json
@description('Name of the embedding model deployment')
param embedDeploymentName string // Set in main.parameters.json

@description('Version of the embedding model to deploy')
// See version availability in this table:
// https://learn.microsoft.com/azure/ai-services/openai/concepts/models#embeddings-models
param embedDeploymentVersion string // Set in main.parameters.json

@description('Sku of the embeddings model deployment')
param embedDeploymentSku string // Set in main.parameters.json

@description('Capacity of the embedding deployment')
// You can increase this, but capacity is limited per model/region, so you will get errors if you go over
// https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits
param embedDeploymentCapacity int // Set in main.parameters.json

@description('Dimensions of the embedding model')
param embedDimensions int // Set in main.parameters.json

@description('Use AI project')
param useAiProject bool = false

@description('Whether to use Application insights or not')
param useApplicationInsights bool // Set in main.parameters.json

var resourceToken = toLower(uniqueString(subscription().id, name, location))
var prefix = '${toLower(name)}-${resourceToken}'
var tags = { 'azd-env-name': name }

var openAIDeploymentName = '${prefix}-openai'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${name}-rg'
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

resource openAIResourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' existing = if (!empty(openAIResourceGroupName)) {
  name: !empty(openAIResourceGroupName) ? openAIResourceGroupName : resourceGroup.name
}

var openAiDeployments = [
  {
  name: chatDeploymentName
  model: {
    format: 'OpenAI'
    name: chatModelName
    version: chatDeploymentVersion
  }
  sku: {
    name: chatDeploymentSku
    capacity: chatDeploymentCapacity
  }
}
{
  name: embedDeploymentName
  model: {
    format: 'OpenAI'
    name: embedModelName
    version: embedDeploymentVersion
  }
  sku: {
    name: embedDeploymentSku
    capacity: embedDeploymentCapacity
  }
}]

module openAI 'core/ai/cognitiveservices.bicep' = if (deployAzureOpenAI) {
  name: 'openai'
  scope: openAIResourceGroup
  params: {
    name: openAIDeploymentName
    location: openAILocation
    tags: tags
    sku: {
      name: 'S0'
    }
    deployments: openAiDeployments
  }
}

module storage 'br/public:avm/res/storage/storage-account:0.9.1' = if (useAiProject) {
  name: 'storage'
  scope: resourceGroup
  params: {
    name: '${take(replace(prefix, '-', ''), 17)}storage'
    location: location
    tags: tags
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    roleAssignments: [
      {
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
    ]
    blobServices: {
      containers: [
        {
          name: 'default'
          publicAccess: 'None'
        }
      ]
      cors: {
        corsRules: [
          {
          allowedOrigins: [
            'https://mlworkspace.azure.ai'
            'https://ml.azure.com'
            'https://*.ml.azure.com'
            'https://ai.azure.com'
            'https://*.ai.azure.com'
            'https://mlworkspacecanary.azure.ai'
            'https://mlworkspace.azureml-test.net'
          ]
          allowedMethods: [
            'GET'
            'HEAD'
            'POST'
            'PUT'
            'DELETE'
            'OPTIONS'
            'PATCH'
          ]
          maxAgeInSeconds: 1800
          exposedHeaders: [
            '*'
          ]
          allowedHeaders: [
            '*'
          ]
        }
      ]
    }
  }
  }
}

module ai 'core/ai/ai-foundry.bicep' = if (useAiProject) {
  name: 'ai'
  scope: resourceGroup
  params: {
    location: 'swedencentral'
    tags: tags
    foundryName: 'aifoundry-${resourceToken}'
    projectName: 'aiproject-${resourceToken}'
    storageAccountName: storage.?outputs.name ?? 'default-storage-account'
    principalId: principalId
  }
}

// USER ROLES
module openAIRoleUser 'core/security/role.bicep' = {
  scope: openAIResourceGroup
  name: 'openai-role-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' // Cognitive Services OpenAI User
    principalType: empty(runningOnGh) ? 'User' : 'ServicePrincipal'
  }
}

module appInsightsReaderRole 'core/security/role.bicep' = if (useApplicationInsights) {
  scope: resourceGroup
  name: 'appinsights-reader-role'
  params: {
    principalId: principalId
    roleDefinitionId: '43d0d8ad-25c7-4714-9337-8ba259a9fe05' // Application Insights Component Reader
    principalType: 'User'
  }
}

module azureAiUserRole 'core/security/role.bicep' = if (useAiProject && resourceGroup.name != openAIResourceGroup.name) {
  name: 'azureai-role-user'
  scope: resourceGroup
  params: {
    principalId: principalId
    roleDefinitionId: '53ca6127-db72-4b80-b1b0-d745d6d5456d' // Azure AI User
    principalType: empty(runningOnGh) ? 'User' : 'ServicePrincipal'
  }
}

module cognitiveServiceSecret './app/key-vault-secrets.bicep' = if (deployAzureOpenAI) {
  name: 'keyvaultsecret-cognitiveservice'
  scope: resourceGroup
  params: {
    rgName: resourceGroup.name
    keyVaultName: keyVault.outputs.name
    name: 'cognitiveServiceKey'
    cognitiveServiceName: openAI.?outputs.name ?? ''
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

module mongoCluster 'core/database/cosmos/mongo/cosmos-mongo-cluster.bicep' = {
  name: 'mongoCluster'
  scope: resourceGroup
  params: {
    name: mongoClusterName
    location: mongoServiceLocation
    tags: tags
    administratorLogin: mongoAdminUser
    administratorLoginPassword: mongoAdminPassword
    storage: 32
    nodeCount: 1
    sku: mongoServiceSku
    allowAzureIPsFirewall: true
  }
}

// Monitor application with Azure Monitor
module monitoring 'core/monitor/monitoring.bicep' = if (useApplicationInsights) {
  name: 'monitoring'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    applicationInsightsName: '${prefix}-appinsights'
    logAnalyticsName: '${take(prefix, 50)}-loganalytics' // Max 63 chars
  }
}

module applicationInsightsDashboard 'app/dashboard.bicep' = if (useApplicationInsights) {
  name: 'application-insights-dashboard'
  scope: resourceGroup
  params: {
    name: '${prefix}-appinsights-dashboard'
    location: location
    applicationInsightsName: useApplicationInsights ? (monitoring.?outputs.applicationInsightsName ?? '') : ''
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

var webAppEnv = {
  OPENAI_CHAT_HOST: openAIChatHost
  OPENAI_EMBED_HOST: openAIEmbedHost
  AZURE_OPENAI_API_VERSION: openAIChatHost == 'azure' ? azureOpenAIAPIVersion : ''
  AZURE_OPENAI_API_KEY: deployAzureOpenAI ? '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=cognitiveServiceKey)' : azureOpenAIKey
  AZURE_OPENAI_ENDPOINT:  !empty(azureOpenAIEndpoint) ? azureOpenAIEndpoint : (deployAzureOpenAI ? openAI.?outputs.endpoint ?? '' : '')
  AZURE_OPENAI_DEPLOYMENT_NAME: deployAzureOpenAI ? openAIDeploymentName : ''
  AZURE_OPENAI_CHAT_MODEL_NAME: openAIChatHost == 'azure' ? chatModelName : ''
  AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: openAIChatHost == 'azure' ? chatDeploymentName : ''
  OPENAICOM_CHAT_MODEL: openAIChatHost == 'openaicom' ? chatModelName : ''
  AZURE_OPENAI_EMBEDDINGS_MODEL_NAME: openAIEmbedHost == 'azure' ? embedModelName : ''
  AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME: openAIEmbedHost == 'azure' ? embedDeploymentName : ''
  OPENAICOM_EMBED_DIMENSIONS: openAIEmbedHost == 'openaicom' ? '1536' : ''
  OPENAICOM_EMBED_MODEL: openAIEmbedHost == 'openaicom' ? 'text-embedding-3-small' : ''
  AZURE_OPENAI_EMBEDDINGS_DIMENSIONS: openAIEmbedHost == 'azure' ? string(embedDimensions) : ''
  APPLICATIONINSIGHTS_CONNECTION_STRING: useApplicationInsights ? (monitoring.?outputs.applicationInsightsConnectionString ?? '') : ''
  AZURE_COSMOS_PASSWORD: '@Microsoft.KeyVault(VaultName=${keyVault.outputs.name};SecretName=mongoAdminPassword)'
  AZURE_COSMOS_CONNECTION_STRING: mongoCluster.outputs.connectionStringKey
  AZURE_COSMOS_USERNAME: mongoAdminUser
  AZURE_COSMOS_DATABASE_NAME: 'CosmicDB'
  AZURE_COSMOS_COLLECTION_NAME: 'CosmicFoodCollection'
  AZURE_COSMOS_INDEX_NAME: 'CosmicIndex'
  OPENAICOM_KEY: !empty(openAIComKey) ? openAIComKey : ''
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
    appSettings: webAppEnv
    keyVaultName: keyVault.outputs.name
    applicationInsightsName: useApplicationInsights ? (monitoring.?outputs.applicationInsightsName ?? '') : ''

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

output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = resourceGroup.name
output WEB_URI string = web.outputs.uri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name

output APPLICATIONINSIGHTS_NAME string = useApplicationInsights ? (monitoring.?outputs.applicationInsightsName ?? '') : ''

output OPENAI_CHAT_HOST string = openAIChatHost
output OPENAI_EMBED_HOST string = openAIEmbedHost
output AZURE_OPENAI_SERVICE string = deployAzureOpenAI ? (openAI.?outputs.name ?? '') : ''
output AZURE_OPENAI_RESOURCE_GROUP string = deployAzureOpenAI ? openAIResourceGroup.name : ''
output AZURE_OPENAI_ENDPOINT string = !empty(azureOpenAIEndpoint)
  ? azureOpenAIEndpoint
  : (deployAzureOpenAI ? openAI.?outputs.endpoint ?? '' : '')
output AZURE_OPENAI_VERSION string = azureOpenAIAPIVersion
output AZURE_OPENAI_CHAT_DEPLOYMENT_NAME string = deployAzureOpenAI ? chatDeploymentName : ''
output AZURE_OPENAI_CHAT_DEPLOYMENT_VERSION string = deployAzureOpenAI ? chatDeploymentVersion : ''
output AZURE_OPENAI_CHAT_DEPLOYMENT_CAPACITY int = deployAzureOpenAI ? chatDeploymentCapacity : 0
output AZURE_OPENAI_CHAT_DEPLOYMENT_SKU string = deployAzureOpenAI ? chatDeploymentSku : ''
output AZURE_OPENAI_CHAT_MODEL_NAME string = deployAzureOpenAI ? chatModelName : ''
output AZURE_OPENAI_EMBED_DEPLOYMENT_NAME string = deployAzureOpenAI ? embedDeploymentName : ''
output AZURE_OPENAI_EMBED_DEPLOYMENT_VERSION string = deployAzureOpenAI ? embedDeploymentVersion : ''
output AZURE_OPENAI_EMBED_DEPLOYMENT_CAPACITY int = deployAzureOpenAI ? embedDeploymentCapacity : 0
output AZURE_OPENAI_EMBED_DEPLOYMENT_SKU string = deployAzureOpenAI ? embedDeploymentSku : ''
output AZURE_OPENAI_EMBED_MODEL_NAME string = deployAzureOpenAI ? embedModelName : ''
output AZURE_OPENAI_EMBED_DIMENSIONS string = deployAzureOpenAI ? string(embedDimensions) : ''

output AZURE_AI_PROJECT string = useAiProject ? (ai.?outputs.projectName ?? '') : ''

output mongoClusterConnectionString string = mongoCluster.outputs.connectionStringKey
output mongoClusterAdminUser string = mongoAdminUser
