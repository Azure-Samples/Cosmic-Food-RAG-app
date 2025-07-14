# RAG chat: Deploying with minimal costs

This AI RAG chat application is designed to be easily deployed using the Azure Developer CLI, which provisions the infrastructure according to the Bicep files in the `infra` folder. Those files describe each of the Azure resources needed, and configures their SKU (pricing tier) and other parameters. Many Azure services offer a free tier, but the infrastructure files in this project do *not* default to the free tier as there are often limitations in that tier.

However, if your goal is to minimize costs while prototyping your application, follow the steps below *before* running `azd up`. Once you've gone through these steps, return to the [deployment steps](../README.md#azd-deployment).

1. Log in to your Azure account using the Azure Developer CLI:

    ```shell
    azd auth login
    ```

1. Create a new azd environment for the free resource group:

    ```shell
    azd env new
    ```

    Enter a name that will be used for the resource group.
    This will create a new folder in the `.azure` folder, and set it as the active environment for any calls to `azd` going forward.

1. Use the free tier of Azure App Service:

    * Set the App Service SKU to the free tier:

        ```shell
        azd env set AZURE_APP_SERVICE_SKU F1
        ```

    Limitation: You are only allowed a certain number of free App Service instances per region. If you have exceeded your limit in a region, you will get an error during the provisioning stage. If that happens, you can run `azd down`, then `azd env new` to create a new environment with a new region.

1. Use the free tier of Azure Cosmos DB for MongoDB vCore:

    * Set the Cosmos DB SKU to the free tier:

        ```shell
        azd env set AZURE_MONGO_SERVICE_SKU Free
        ```

    Limitation: The free tier of Cosmos DB is only available in certain regions. If you get an error during provisioning, you may need to change the region for the cosmos DB service. You can do this by running:

      ```shell
      azd env set AZURE_MONGO_SERVICE_REGION <your-region>
      ```

    Replace `<your-region>` with a region that supports the free tier of Cosmos DB. You can find a list of supported regions in the [Azure Cosmos DB documentation](https://learn.microsoft.com/azure/cosmos-db/free-tier).

1. Turn off Azure Monitor (Application Insights):

    ```shell
    azd env set AZURE_USE_APPLICATION_INSIGHTS false
    ```

    Application Insights is quite inexpensive already, so turning this off may not be worth the costs saved,
    but it is an option for those who want to minimize costs.

1. Once you've made the desired customizations, you can run `azd up` to build, package, and deploy your customizations to Azure. We recommend using "eastus" as the region, for availability reasons.
