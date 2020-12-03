# sam-media-convert

## Description
Workflow to run a MediaCovert job on an newly created s3 file.  The original file will be removed upon successful MediaConvert job run.  

## Parameters
* BucketName: the name of the bucket.  For example, if the bucket you choose is: `s3://media-convert/` - the BucketName will be `media-convert`.
* AddtionalBucketName: (optional) if you want to add a 2nd bucket.  Note, you will need to manually add the trigger to the s3 bucket if you wish to use this feature.  Just copy the same s3 event trigger defined by the original bucket.  This gives you the ability to run mediaconvert jobs in a previously created bucket (managed outside of the sam app).
* JobTemplateName: the name of the MediaConvert template you created in the MediaConvert service.  For more information, see: https://docs.aws.amazon.com/mediaconvert/latest/ug/creating-template-from-scratch.html
* DestinationRelativePath: will store the resulting mediaconvert file in this relative directory.  If you wish it to be inside the same directory, leave this blank.
* Timeout: the number of seconds to set the lambda timeout.  Default is set to 300 seconds.  Max value permitted by lambda is 900 seconds.

## Caveats
* The `Bucket`, `AddtionalBucket`, and `JobTemplate` must reside in the same region as `sam-media-convert`
* The bucket defined by BucketName parameter will be created.  It's not possible to use a pre-existing bucket with this parameter.  If you wish to use a pre-existing bucket, set the AddtionalBucketName to the pre-existing bucket and create the s3 event trigger manually (set to the same lambda function that was created in the BucketName bucket.


## Developer Notes
### Build
`sam build -u`

## Test Locally
This is an example, you'll have to provide your own event that contains a path to a real file.
`sam local invoke --region=us-west-2 --profile=administrator --parameter-overrides=ParameterKey=BucketName,ParameterValue=bucket-stage --force-image-build "MediaConvertFunction" -e events/file_uploaded.sns.json`

### Unit Tests
#### Setup
##### Install Modules venv
``` shell
source ~/.virtualenvs/elpy-rpc-venv/bin/activate
pip3 pytest boto3 pytest-mock moto
deactivate
```
##### Update sys.path in all tests
`sys.path.append('${PROJECT_DIR}/sam-media-convert/')`

#### Run Tests
* `cd ${PROJECT_DIR}`
* `pytest -v tests` 

### Validate
`sam validate --region=$REGION --profile=$PROFILE -t template.yaml`

### Deploy
``` shell
sam build --use-container
sam deploy --region=$REGION --profile=$PROFILE --guided

```
