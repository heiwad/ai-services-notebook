NOTEBOOK_ARN=$(sudo jq '.ResourceArn' /opt/ml/metadata/resource-metadata.json --raw-output)
STACK_NAME=$(aws sagemaker list-tags --resource-arn $NOTEBOOK_ARN --query "Tags[?Key=='aws:cloudformation:stack-name'].Value" --output text)
BUCKET_NAME=$(aws cloudformation describe-stack-resources --stack-name $STACK_NAME --query "StackResources[?ResourceType=='AWS::S3::Bucket'][PhysicalResourceId]" --output text)
REGION=$(curl 169.254.169.254/latest/meta-data/placement/region)
echo $BUCKET_NAME,$REGION