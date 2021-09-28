# Cloud One Application Security with InSekureStore

- [Cloud One Application Security with InSekureStore](#cloud-one-application-security-with-insekurestore)
  - [Install Node](#install-node)
  - [Update IAM Settings for the Workspace](#update-iam-settings-for-the-workspace)
  - [Install Serverless](#install-serverless)
  - [Role and User](#role-and-user)
    - [Create serverless AWS user](#create-serverless-aws-user)
    - [Create a Role for Lambda, S3, RDS](#create-a-role-for-lambda-s3-rds)
  - [Deploy the Serverless InSekureStore](#deploy-the-serverless-insekurestore)
    - [Get the sources](#get-the-sources)
    - [Configure](#configure)
    - [Deploy](#deploy)
    - [Upload Some Files](#upload-some-files)
    - [Access the Serverless Application](#access-the-serverless-application)
    - [Remove the InSekureStore](#remove-the-insekurestore)
  - [Cloud One Application Security Configuration](#cloud-one-application-security-configuration)
    - [Protection Policy](#protection-policy)
    - [SQL Injection Policy Configuration](#sql-injection-policy-configuration)
    - [Illegal File Access Policy Configuration](#illegal-file-access-policy-configuration)
    - [Remote Command Execution Policy Configuration](#remote-command-execution-policy-configuration)
  - [InSekureStore - Attacks](#insekurestore---attacks)
    - [SQL Injection](#sql-injection)
    - [Directory Traversal](#directory-traversal)
    - [Remote Command Execution](#remote-command-execution)
  - [Support](#support)
  - [Contribute](#contribute)

The app is to be deployed by `serverless`.

## Install Node

```sh
curl -sL https://deb.nodesource.com/setup_14.x | sudo -E bash -
sudo apt-get install -y nodejs
```

If you get the error `E: Cloud not get lock /var/lib/dpkg frontend lock...` you need to wait 2 to 3 minutes for the background task to complete. Simply retry the `apt-get install`. Then check the node version with

```sh
nodejs --version
```

```text
v14.16.1
```

## Update IAM Settings for the Workspace

- Click the gear icon (in top right corner), or click to open a new tab and choose “Open Preferences”
- Select AWS SETTINGS
- Turn off AWS managed temporary credentials
- Close the Preferences tab

Install AWS CLI.

```sh
# sudo apt install -y awscli
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

## Install Serverless

```sh
npm install -g serverless
serverless --version
```

```text
Framework Core: 2.37.0
Plugin: 4.5.3
SDK: 4.2.2
Components: 3.9.0
```

## Role and User

### Create serverless AWS user

Services in AWS, such as AWS Lambda, require that you provide credentials when you access them to ensure that you have permission to access the resources owned by that service. To accomplish this AWS recommends that you use AWS Identity and Access Management (IAM).

1. Login to your AWS account and go to the Identity & Access Management (IAM) page.
2. Follow this deep link to create the serverless AWS user: <https://console.aws.amazon.com/iam/home?#/users$new?step=review&accessKey&userNames=serverless-admin&groups=Administrators>
3. Confirm that Group `Administrators` is listed, then click `Create user` to view permissions.
4. View and copy the API Key & Secret to a temporary place. You'll need it in the next step.

### Create a Role for Lambda, S3, RDS

1. Create a role by following this deep link: <https://console.aws.amazon.com/iam/home?#/roles$new?step=review&commonUseCase=Lambda%2BLambda&selectedUseCase=Lambda&policies=arn:aws:iam::aws:policy%2FAmazonS3FullAccess&policies=arn:aws:iam::aws:policy%2FAWSLambdaFullAccess&policies=arn:aws:iam::aws:policy%2FAmazonEC2FullAccess&policies=arn:aws:iam::aws:policy%2FAmazonRDSFullAccess>
2. Without chaning anything, press `Next: Permissions`, `Next: Tags`, `Next: Review`.
3. Set the Role name to `serverless-lambda-s3-role`, Press `Create` and note the ARN.

## Deploy the Serverless InSekureStore

### Get the sources

Do a git clone:

```sh
git clone https://github.com/mawinkler/c1-app-sec-insekurestore.git
cd c1-app-sec-insekurestore
```

There is a `serverless.yml` and a `variables.yml`.
The `variables.yml` is included by the `serverless.yml` via a

```yaml
custom:
  variables: ${file(./variables.yml)}
```

No changes required in `serverless.yml`, a few within `variables.yml`

### Configure

Open the `variables.yml` in the Cloud9 editor and set your Application Security key and secret, Cloud One region and aws region and role.

```yaml
# Cloud One Application Security Configs
# Your applicytion group credentials
TREND_AP_KEY: <key>
TREND_AP_SECRET: <secret>
# Don't change!
AWS_LAMBDA_EXEC_WRAPPER: /opt/trend_app_protect
# Your Cloud One Region, e.g.
# TREND_AP_HELLO_URL: https://agents.trend-us-1.application.cloudone.trendmicro.com/
TREND_AP_HELLO_URL: https://agents.<region>.application.cloudone.trendmicro.com/
# Leave the rest
TREND_AP_READY_TIMEOUT: 30
TREND_AP_TRANSACTION_FINISH_TIMEOUT: 10
TREND_AP_MIN_REPORT_SIZE: 1
TREND_AP_INITIAL_DELAY_MS: 1
TREND_AP_MAX_DELAY_MS: 100
TREND_AP_HTTP_TIMEOUT: 5
TREND_AP_PREFORK_MODE: True
TREND_AP_CACHE_DIR: /tmp/trend_cache

# Lambda Function Configs
# Target Region for the application, e.g.
# REGION: eu-west-2
REGION: <region>
S3_BUCKET: insekures3-${file(s3bucketid.js):bucketId}
LAYER: arn:aws:lambda:${self:custom.variables.REGION}:800880067056:layer:CloudOne-ApplicationSecurity-python:1
# The ARN of the role you created above, e.g.
# ROLE: arn:aws:iam::XXXXXXXXXXXX:role/serverless-lambda-s3-role
ROLE: <role-arn>

DB_NAME: insekuredb
DB_USER: super_insekure
DB_PASSWORD: ZneaZl4RMSbOYpxR06oE
DB_HOST:
  Fn::GetAtt: [Cluster, Endpoint.Address]
DB_PORT:
  Fn::GetAtt: [Cluster, Endpoint.Port]
...
```

### Deploy

Install the python requirements for serverless and ignore the warnings.

```sh
serverless plugin install --name serverless-python-requirements
```

Configure serverless AWS provider credentials

```sh
export AWS_KEY=<API KEY OF SERVERLESS USER CREATED ABOVE>
export AWS_SECRET=<API SECRET KEY OF SERVERLESS USER CREATED ABOVE>

serverless config credentials \
  --provider aws \
  --key ${AWS_KEY} \
  --secret ${AWS_SECRET} \
  -o
```

And deploy

```sh
serverless deploy
```

If everything is successful you will get a link to your lambda driven web application.

```text
...
Service Information
service: insekure-store
stage: dev
region: eu-central-1
stack: insekure-store-dev
resources: 75
api keys:
  None
endpoints:
  GET - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/
  GET - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/{file}
  POST - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/is_valid
  GET - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/list
  GET - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/get_file
  GET - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/read_file
  POST - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/write_file
  POST - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/delete_file
  POST - https://ocwnfvuhg9.execute-api.eu-central-1.amazonaws.com/dev/auth
functions:
  index: insekure-store-dev-index
  static: insekure-store-dev-static
  is_valid: insekure-store-dev-is_valid
  list: insekure-store-dev-list
  get_file: insekure-store-dev-get_file
  read_file: insekure-store-dev-read_file
  write_file: insekure-store-dev-write_file
  delete_file: insekure-store-dev-delete_file
  auth: insekure-store-dev-auth
  db: insekure-store-dev-db
layers:
  None
```

Before accessing the app, you need to initialize the database

```sh
serverless invoke -f db -l
```

```text
"DB Migrated Sucessfully"
```

### Upload Some Files

We're going to upload sample files to the stores bucket. This is named `insekures3-`SOMETHING with `Public` access.

```sh
export STORE_BUCKET=$(aws s3 ls | sed -n 's/.*\(insekures3.*\)/\1/p')
for f in kubernetes.* ; do aws s3 cp $f s3://${STORE_BUCKET}/$f ; done
```

### Access the Serverless Application

You get the URL from the output above, ServiceEndpoint.

Default Credentials

```text
User: admin
Pass: admin
```

The first authentication can likely fail, since the database cluster might not be ready or in running state. This will happen always when you're going to use the app later on, since for cost saving reasons, the cluster suspends automatically after 90 minutes. Additionally, our Application Security layers need to be loaded. So if you're going to use this application for customer demos, play with it a little before the demo.

### Remove the InSekureStore

```sh
serverless remove
sls remove --aws-profile default
```

## Cloud One Application Security Configuration

### Protection Policy

Enable all policies in your group configuration. When you start playing with the app, maybe have them in `Report` mode and switch later to `Block`.

### SQL Injection Policy Configuration

Turn on all controls

### Illegal File Access Policy Configuration

Leave everythin turned on

### Remote Command Execution Policy Configuration

Add the following rule on top of the preconfigured one:

```text
ls -l "/tmp/*.*" -b              <-- Allow
.*                              <-- Block
```

## InSekureStore - Attacks

### SQL Injection

At the login screen

```text
E-Mail: admin
```

```text
Password: 1'or'1'='1
```

*Application Security Protection by `SQL Injection - Always True`*

### Directory Traversal

URL

```text
...dev#/browser?view=../../../etc/passwd
```

### Remote Command Execution

Go to `Mime Type Params` and change to

```text
-b && whoami
```

or

```text
-b && uname -a
```

Within the details of a text file you will see the output of your command.

*Application Security Protection by `Remote Command Execution` or `Malicious Payload`*

## Support

This is an Open Source community project. Project contributors may be able to help, depending on their time and availability. Please be specific about what you're trying to do, your system, and steps to reproduce the problem.

For bug reports or feature requests, please [open an issue](../../issues). You are welcome to [contribute](#contribute).

Official support from Trend Micro is not available. Individual contributors may be Trend Micro employees, but are not official support.

## Contribute

I do accept contributions from the community. To submit changes:

1. Fork this repository.
1. Create a new feature branch.
1. Make your changes.
1. Submit a pull request with an explanation of your changes or additions.

I will review and work with you to release the code.
