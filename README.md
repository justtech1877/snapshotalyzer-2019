# snapshotalyzer-2019

Demo project to manage AWS EC2 volume snapshots.

## CreateBucketConfiguration

This project is a demo, and uses boto3 to manage
AWS EC2 instance volume snapshots.

## Configuring

Shotty uses the configuration file created by the AWS cli, e.g.

`aws configure --profile boto3user`

## Running

`pipenv run python shotty/shotty.py <command>
<--project=PROJECT>`

*command* is list, start or stop
*--project* is optional
