---
name: Cosmic Food with Azure OpenAI and Azure Cosmos DB for MongoDB vCore
description: A Demo application for a streamlined ordering system tailored for various food categories. It allows users to request customized meals, such as "high protein dishes," with recommendations provided from our database. Users can further customize their choices before sending their orders from the app to the restaurant, including delivery details.
languages:
- python
- typescript
- bicep
- azdeveloper
products:
- azure
- azure-app-service
- azure-openai
- cosmos-db
- mongodb-vcore
page_type: sample
urlFragment: build-24-langchain-vcore
---

# Cosmic Food with Azure OpenAI and Azure Cosmos DB for MongoDB vCore

 A Demo application for a streamlined ordering system tailored for various food categories. It allows users to request customized meals, such as "high protein dishes," with recommendations provided from our database. Users can further customize their choices before sending their orders from the app to the restaurant, including delivery details. A unique feature of our system is its ability to remember user preferences for future orders, using vCore to store that data. With the help of Langchain, this setup can be easily adapted by ISVs with minimal modifications needed for other food chains.

![image](https://github.com/khelanmodi/build-24-langchain-vcore/assets/64026625/618397af-2ae9-4b44-9d38-d6bd3fe75098)


## How to use?

1. Create the following resources on Microsoft Azure:

    - Azure Cosmos DB for MongoDB vCore cluster. See the [Quick Start guide here](https://techcommunity.microsoft.com/t5/educator-developer-blog/build-rag-chat-app-using-azure-cosmos-db-for-mongodb-vcore-and/ba-p/4055852#:~:text=RAG%20Chat%20Application-,Step%201%3A%20Create%20an%20Azure%20Cosmos%20DB%20for%20MongoDB%20vCore%20Cluster,-In%20this%20step).
    - Azure OpenAI resource with:
        - Embedding model deployment. (ex. `text-embedding-ada-002`) See the [guide here](https://techcommunity.microsoft.com/t5/educator-developer-blog/build-rag-chat-app-using-azure-cosmos-db-for-mongodb-vcore-and/ba-p/4055852#:~:text=to%20it%20later.-,Step%202%3A%C2%A0Create%20an%20Azure%20OpenAI%20resource%20and%20Deploy%20chat%20and%20embedding%20Models,-In%20this%20step).
        - Chat model deployment. (ex. `gpt-35-turbo`)

1. Open the repository in GitHub Codespaces:

    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/khelanmodi/build-24-langchain-vcore?devcontainer_path=.devcontainer/devcontainer.json)

1. 📝 Start here 👉 [CBD_Mongo_vCore.ipynb](./CBD_Mongo_vCore.ipynb)

## Local development

1. **Download the project starter code locally**

    ```bash
    git clone https://github.com/khelanmodi/build-24-langchain-vcore.git
    cd build-24-langchain-vcore
    ```

1. **Initialize and activate a virtualenv using:**

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

    >**Note** - In Windows, the `.venv` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:

    ```bash
    source .venv/Scripts/activate
    ```

1. **Install the development dependencies as an editable package:**

    ```bash
    python3 -m pip install -e 'src[dev]'
    ```

1. **Run the [notebook](./CBD_Mongo_vCore.ipynb) to generate the .env file and test out everything**

### Running the website locally

1. **Execute the following command to build the website inside the `frontend/` folder and return to the root folder**

    ```bash
    cd ./frontend
    npm install && npm run build
    cd ../
    ```

1. **Execute the following command in your terminal to start the quart app**

    ```bash
    export QUART_APP=src.quartapp
    export QUART_ENV=development
    export QUART_DEBUG=true
    quart run -h localhost -p 50505
    ```

    **For Windows, use [`setx`](https://learn.microsoft.com/windows-server/administration/windows-commands/setx) command shown below:**

   ```powershell
    setx QUART_APP src.quartapp
    setx QUART_ENV development
    setx QUART_DEBUG true
    quart run -h localhost -p 50505
    ```

1. **Verify on the Browser**

Navigate to project homepage [http://127.0.0.1:50505/](http://127.0.0.1:50505/) or [http://localhost:50505](http://localhost:50505)

## `azd` Deployment

![architecture-thumbnail](https://github.com/khelanmodi/build-24-langchain-vcore/assets/64026625/4c5845d4-d4ab-4342-b559-60ba65943f45)

This repository is set up for deployment on Azure App Service (w/Azure Cosmos DB for MongoDB vCore) using the configuration files in the `infra` folder.

To deploy your own instance, follow these steps:

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/)

1. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd).

1. Login to your Azure account:

    ```shell
    azd auth login
    ```

1. Initialize a new `azd` environment:

    ```shell
    azd init
    ```

    It will prompt you to provide a name (like "quart-app") that will later be used in the name of the deployed resources.

1. Provision and deploy all the resources:

    ```shell
    azd up
    ```

    It will prompt you to login, pick a subscription, and provide a location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location (like to "centralus") can help, as there may be availability constraints for some of the resources.

When azd has finished deploying, you'll see an endpoint URI in the command output. Visit that URI to browse the app! 🎉

> [!NOTE]
> If you make any changes to the app code, you can just run this command to redeploy it:
>
> ```shell
> azd deploy
> ```
>

### Add the Data

1. Open the [Azure portal](https://portal.azure.com) and sign in.

1. Navigate to your App Service page.

    ![Azure App service screenshot with the word SSH highlighted in a red box.](https://github.com/john0isaac/rag-semantic-kernel-mongodb-vcore/assets/64026625/759db6be-604e-433c-878e-b6c3de671fd1)

1. Select **SSH** from the left menu then, select **Go**.

1. In the SSH terminal, run `python ./scripts/add_data.py  --file="./data/food_items.json"`.
