import { Construct } from 'constructs';
import { aws_lambda as lambda } from 'aws-cdk-lib';
import { PythonFunction, PythonLayerVersion } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_iam as iam } from 'aws-cdk-lib';
import { aws_logs as logs } from 'aws-cdk-lib';
import { aws_s3 as s3 } from 'aws-cdk-lib';
import { aws_s3_deployment as s3deploy } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';

export interface Chapter10Props {

}

export class Chapter10 extends Construct {
  constructor(scope: Construct, id: string, props: Chapter10Props) {
    super(scope, id);


    const numpyLayer = new PythonLayerVersion(this, 'NumpyLayer', {
      entry: 'lambda/layer/numpy',
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12]
    })

    const checkCosFunction = new PythonFunction(this, 'CheckCosFunction', {
      functionName: 'checkCosFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter10-check-cos',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      layers: [numpyLayer]
    });


    checkCosFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));


    const lambdaUrl = checkCosFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'CheckCosLambdaEndpoint', {
      value: lambdaUrl.url
    })



    const textSearchFunction = new PythonFunction(this, 'TextSearchFunction', {
      functionName: 'textSearchFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter10-text-search',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      layers: [numpyLayer]
    });


    textSearchFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));


    const textSearchFunctionUrl = textSearchFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'textSearchFunctionEndpoint', {
      value: textSearchFunctionUrl.url
    })



    const imageSearchBucket = new s3.Bucket(this, 'ImageSearchBucket', {
      autoDeleteObjects: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    })

    // imageをデプロイ
    new s3deploy.BucketDeployment(this, 'ImageDeploy', {
      sources: [s3deploy.Source.asset("./sample/input_image")],
      destinationBucket: imageSearchBucket,
    })




    const imageSearchFunction = new PythonFunction(this, 'ImageSearchFunction', {
      functionName: 'imageSearchFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter10-image-search',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      environment: {
        'BUCKET_NAME': imageSearchBucket.bucketName
      },
      layers: [numpyLayer]
    });

    imageSearchBucket.grantRead(imageSearchFunction)
    imageSearchFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'))


    const imageSearchLambdaUrl = imageSearchFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'ImageSearchFunctionEndpoint', {
      value: imageSearchLambdaUrl.url
    })


  }
}