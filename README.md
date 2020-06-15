# c1-app-sec-insekurestore
The app is to be deployed by `serverless`.

## Serverless
### Prerequisites
**Install Node**
```shell
curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
```
```
v13.11.0
```
**Install AWS cli**
```shell
sudo apt install -y awscli
aws configure
```
**Install Serverless**
```shell
sudo npm install -g serverless
serverless --version
```
```
Framework Core: 1.67.0
Plugin: 3.6.0
SDK: 2.3.0
Components: 2.22.3
```
Now, at least install the python requirements for serverless.
```shell
sudo serverless plugin install --name serverless-python-requirements
```
**Next, create a serverless AWS user**

Services in AWS, such as AWS Lambda, require that you provide credentials when you access them to ensure that you have permission to access the resources owned by that service. To accomplish this AWS recommends that you use AWS Identity and Access Management (IAM).

1. Login to your AWS account and go to the Identity & Access Management (IAM) page.

2. Click on Users and then Add user. Enter a name in the first field to remind you this User is related to the Serverless Framework, like serverless-admin. Enable Programmatic access by clicking the checkbox. Click Next to go through to the Permissions page. Click on Attach existing policies directly. Search for and select `AdministratorAccess` then click Next: Review. Check to make sure everything looks good and click Create user.

3. View and copy the API Key & Secret to a temporary place. You'll need it in the next step.

**Configure Serverless**

Either
```shell
export AWS_ACCESS_KEY_ID=<your-key-here>
export AWS_SECRET_ACCESS_KEY=<your-secret-key-here>
```
Or
```shell
serverless config credentials --provider aws --key <your-key-here> --secret <your-secret-key-here>
```
Or
```shell
aws configure
```
I use the last variant.

**Create a Role for Lambda, S3, RDS**

Create a role with the following permissions:
```
AmazonS3FullAccess
AWSLambdaFullAccess
AmazonEC2FullAccess
AmazonRDSFullAccess
```
and name it `trend-demo-lambda-s3-role`. Remember the ARN.

## Deploy c1-app-sec-insekurestore
There is a `serverless.yml` and a `variables.yml`.
The `variables.yml` is included by the `serverless.yml` via a
```
custom:
  variables: ${file(./variables.yml)}
```
No changes required in `serverless.yml`, a few within `variables.yml`

**Modify the `variables.yml`**
```shell
vi variables.yml
```
Set your Application Security key and secret, region and role.
```
# Cloud One Application Security Configs
TREND_AP_KEY: <your-ap-key-here>
TREND_AP_SECRET: <your-secret-key-here>
TREND_AP_READY_TIMEOUT: 30

# Lambda Function Configs
REGION: <your-region-here>
S3_BUCKET: insecures3-${file(s3bucketid.js):bucketId}
LAYER: arn:aws:lambda:${self:custom.variables.REGION}:321717822244:layer:DS-AppProtect-DEV-python3_6:11
ROLE: <your-just-created-role-arn-here>
```

**Deploy**
```shell
sls -v deploy --stage dev --aws-profile default
sls invoke -f db -l --aws-profile default
```
If everything is successful you will get a link to your lambda driven web application.
```
Service Information
service: insekure-store
stage: dev
region: eu-central-1
stack: insekure-store-dev
resources: 76
api keys:
  None
endpoints:
  GET - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/
  GET - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/{file}
  POST - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/is_valid
  GET - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/list
  GET - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/get_file
  GET - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/read_file
  POST - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/write_file
  POST - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/delete_file
  POST - https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev/auth
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

Stack Outputs
ServiceEndpoint: https://3ovy8p00n9.execute-api.eu-central-1.amazonaws.com/dev
ServerlessDeploymentBucketName: insekure-store-dev-serverlessdeploymentbucket-dopk8qr47fi2

Serverless: Run the "serverless" command to setup monitoring, troubleshooting and testing.
```
Default Credentials
```
User: admin
Pass: admin
```

## Demo Cloud1 Application Security
### Protection Policy
Enable all policies in your group configuration. When you start playing with the app, maybe have them in `Report` mode and switch later to `Block`.

### SQL Injection Policy Configuration
Turn on all controls

### Illegal File Access Policy Configuration
Leave everything turned on

### Remote Command Execution Policy Configuration
Add the following rule on top of the preconfigured one:
```
file "/tmp/*.*" -b              <-- Allow
.*                              <-- Block
```

### Open Redirect Policy Configuration


## Attacks
### SQL Injection
At the login screen
```
E-Mail: 1'or'1'='1
```
```
Password: <any>
```

*Application Security Protection by `SQL Injection - Always True`*

### Directory Traversal
URL
```
...dev#/browser?view=../../../etc/passwd
```

*Application Security Protection by `Malicious Payload`*

### Shellshock
Open a terminal window and paste in the following (ShellShock) exploit:
```
curl -H "User-Agent: () { :; }; /bin/eject" <ServiceEndpoint>
```

*Application Security Protection by `Malicious Payload`*

### Illegal File Access
Click on any uploaded file in edit mode and replace the name with
```
evil.py
```
Click `save`. That will create a new file in the app.

*Application Security Protection by `Illegal File Access`*

### Remote Command Execution
Go to `Mime Type Params` and change to
```
-b && whoami
```
or
```
-b && uname -a
```
Within the details of a text file you will see the output of your command.

*Application Security Protection by `Remote Command Execution`*

### Open Redirect
Redirect hooks work at framework level. This demo app is not built using a framework like most lambda application and hence we do not have a framework API to hook.

*Application Security Protection by `Open Redirect`*

### Malicious File Upload
The file upload is from browser to s3 bucket. The contents of the file never reaches the lambda function. The lambda function only provides signed urls to the browser for direct uploads. Therefore the current functionality of Application Security does not work here.
We will have file access protection for such AWS APIs in future.

*Application Security Protection by `Malicious File Upload`*

## Additional Info
### Lambda Layers for Application Security
One of the Lambda layers will be selected according to your region:
```
Python3.6 Lambda Layers:
arn:aws:lambda:eu-north-1:321717822244:layer:DS-AppProtect-DEV-python3_6:12
arn:aws:lambda:ap-south-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:eu-west-3:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:eu-west-2:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:eu-west-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:ap-northeast-2:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:ap-northeast-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:sa-east-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:ca-central-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:ap-southeast-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:ap-southeast-2:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:eu-central-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:us-east-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:us-east-2:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:us-west-1:321717822244:layer:DS-AppProtect-DEV-python3_6:11
arn:aws:lambda:us-west-2:321717822244:layer:DS-AppProtect-DEV-python3_6:11
```

### Remove
```shell
sls remove --aws-profile default
```
