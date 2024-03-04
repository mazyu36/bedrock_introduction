import { Construct } from 'constructs';
import { aws_lambda as lambda } from 'aws-cdk-lib';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_iam as iam } from 'aws-cdk-lib';
import { aws_logs as logs } from 'aws-cdk-lib';
import { aws_lambda_nodejs as nodejs } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';

export interface Chapter7Props {

}

export class Chapter7 extends Construct {
  constructor(scope: Construct, id: string, props: Chapter7Props) {
    super(scope, id);


    const streamingFunction = new PythonFunction(this, 'StreamingFunction', {
      functionName: 'streamingFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter7-python',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY
    });


    streamingFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));


    const streamingFunctionNode = new nodejs.NodejsFunction(this, 'StreamingFunctionNode', {
      functionName: 'streamingFunctionNode',
      runtime: lambda.Runtime.NODEJS_20_X,
      entry: 'lambda/chapter7-node/index.mjs',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY
    });

    streamingFunctionNode.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));

    const lambdaUrl = streamingFunctionNode.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.RESPONSE_STREAM
    })

    new cdk.CfnOutput(this, 'StreamingResponseLambdaEndpoint', {
      value: lambdaUrl.url
    })


  }
}