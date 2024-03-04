import { Construct } from 'constructs';
import { aws_lambda as lambda } from 'aws-cdk-lib';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_iam as iam } from 'aws-cdk-lib';
import { aws_s3 as s3 } from 'aws-cdk-lib';
import { aws_logs as logs } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';

export interface Chapter6Props {

}

export class Chapter6 extends Construct {
  constructor(scope: Construct, id: string, props: Chapter6Props) {
    super(scope, id);

    // 画像保存用バケット
    const imageBucket = new s3.Bucket(this, 'ImageBucket', {
      autoDeleteObjects: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    })

    // 画像生成
    const generateImageFunction = new PythonFunction(this, 'GenerateImageFunction', {
      functionName: 'generateImageFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter6-image',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      environment: {
        'BUCKET_NAME': imageBucket.bucketName
      },
      logRetention: logs.RetentionDays.ONE_DAY
    });

    generateImageFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));
    imageBucket.grantReadWrite(generateImageFunction)


    const lambdaUrl = generateImageFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'GenerateImageLambdaEndpoint', {
      value: lambdaUrl.url
    })


    // SDXLによるイメージ編集
    const editImageSdxlFunction = new PythonFunction(this, 'EditImageSdxlFunction', {
      functionName: 'editImageSdxlFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter6-edit-sdxl',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      environment: {
        'BUCKET_NAME': imageBucket.bucketName
      },
    });

    editImageSdxlFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));
    imageBucket.grantReadWrite(editImageSdxlFunction)


    const editImageSdxlFunctionUrl = editImageSdxlFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'EditImageSdxlFunctionEndpoint', {
      value: editImageSdxlFunctionUrl.url
    })


    // Titanによるイメージ編集
    const editImageFunction = new PythonFunction(this, 'EditImageFunction', {
      functionName: 'editImageFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter6-edit-titan',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      environment: {
        'BUCKET_NAME': imageBucket.bucketName
      },
    });

    editImageFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));
    imageBucket.grantReadWrite(editImageFunction)


    const editImageFunctionUrl = editImageFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'EditImageFunctionEndpoint', {
      value: editImageFunctionUrl.url
    })



  }
}