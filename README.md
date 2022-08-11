
# finops-report-automation

This repository contains a script that creates automated excel reports using the API of Cloudability. It includes the recommendations to rightsize or terminate EC2, RDS, S3 and EBS resources.

## Installation

This package uses [Poetry](https://python-poetry.org/docs/) to install and define all dependencies. If you have poetry installed, just run:

```shell
poetry install
poetry shell # To activate the virtualenv created by poetry
```

## Configuration

### Environmental variables

There are two environmental variables that need to be set for the script to work

| Environment Variable | Description                                                                           |
| -------------------- | ------------------------------------------------------------------------------------- |
| API_KEY              | Required. Your CloudaAbility API key                                                  |
| REPORTINGS_PATH      | Optional. The folder where the reports will be saved to. Defaults to ./reports           |
| CONFIG_PATH          | Optional. The folder where the configuration files are located. Defaults to ./config. |
| BUCKET_NAME          | Optional. S3 to upload reports to. Not setting this variable will disable upload.     |
| USE_LOCAL_DATA       | Optional. Use local files containing json data instead of the API.                    |
| DEBUG                | Optional. Display debug information.                                                  |

### Configuration files

There are 3 configuration files that need to be in place in order for the script to make the correct API calls and map the relevant
information to specific projects. The config.yaml is needed for general recommendations about your resource, the amortized_cost_config.yaml is needed for the general overview sheet of each project as well as the cross-project overview. 

**Example files** can be found under `./example_configs/`. **Copy and create a new** file on the `CONFIG_PATH` folder.

| File                       | Description                                                                                                                                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| accountMapping.xlsx        | **Required**. Used to map AWS Account IDs to internal project names (e.g: project1 -> 1239585). *Note*: This file should be removed and replaced with a DB connection to query the project names |
| config.yaml                | **Required**. Used to specify filters to retrieve resource specific recommendations from CloudAbility's AWS Rightsizing API                                                                                                        |
| amortized_cost_config.yaml | **Required**. Used to specify filters to retrieve the amortized data from CloudAbility's AWS Amortized API                                                                                       |

## Usage

Once the enviromental variables are configured you can create the reports by running:

```shell
make run
# or
python -m finops_report_automation.main
```

Based on the configuration you defined inside the configuration files you should be able to see the reports generated inside the `REPORTINGS_PATH` folder.

<img width="1292" alt="image" src="https://user-images.githubusercontent.com/13739932/167629155-fc729005-497f-4484-8542-711c5933cb4f.png">
Note: Project names were annonymized

## AWS integration

This script features an optional integration in AWS. It allows you to upload your project reports, cross-project summaries as well as the raw API data to a S3 bucket.

<img width="1292" alt="image" src="https://user-images.githubusercontent.com/48791711/172865109-7a4e392c-4dfc-4f80-95e9-60c36ef68c48.png">

The folder structure will be as follows:

```
├── 2022
│   ├── 01
│   │   ├── 22
|   |   |   ├── Project reports
|   |   |   |   ├── project_01.xlsx
|   |   |   |   ├── project_02.xlsx
|   |   |   ├── cross_project_overview.xlsx
|   |   |   ├── API Response
|   |   |   |   ├── <resource>_api.json
|   |   |   |   ├── armotized_cost_api.json
│   ├── ...
│   ├── 12
```

To run the container we propose Amazon ECS + Fargate. In contrast to AWS Lambda we don't have to alter application code to run it. This also means we can still run the container locally. With the AWS SDK we can still other AWS services like S3.

### Configuration

Prerequisite:
- S3 bucket to store data in
- IAM role including two permission policies:
  - AmazonECSTaskExecutionRolePolicy
  - Policy with _s3:PutObject & s3:GetObject_ allowed on S3 bucket.
  - An ECR

Go to Amazon ECS and create a task definition. Add your Image URI and the *API_KEY & BUCKET_NAME* environmental variables.
For Task Role select your IAM role with ECS and S3 policies.
The policies you need depend on the SDK calls you make in the container. For the moment only upload to S3 is supported.
**SQS calls need additional policies.**

Next we will create a cluster provide an environment to run the task in.
After you've created a cluster and a task definition, you can create a trigger for your task. We accomplish this via an Amazon EventBridge Rule. See [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/scheduled_tasks.html) for the official documentation. 

## Test

To run the test suite, open a shell with the activated virtualenvironment and run the following:

```shell
pytest
```

This should automatically run all the tests located inside the `tests` folder

## Linters and style check

It's possible to manual check the linting and styling of the code by running:

```shell
make flake
```

## Docker

You can also generate your reports using a Docker container. Run the following:

```shell
docker build . -t reports

docker run -e API_KEY=<your-key-here> -e REPORTINGS_PATH=/reports -v <local-report-directory>:/reports reports 
```
