param keyVaultName string
param rgName string

param name string
param cognitiveServiceName string

module keyVaultSecretsOpenai '../core/security/keyvault-secret.bicep' = {
  name: 'openAIKey'
  params: {
    name: name
    keyVaultName: keyVaultName
    secretValue: listKeys(resourceId(subscription().subscriptionId, rgName, 'Microsoft.CognitiveServices/accounts', cognitiveServiceName), '2023-05-01').key1
  }
}
