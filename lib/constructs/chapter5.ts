import { Construct } from 'constructs';
import { aws_lambda as lambda } from 'aws-cdk-lib';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_iam as iam } from 'aws-cdk-lib';
import { aws_logs as logs } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';

export interface Chapter5Props {

}

export class Chapter5 extends Construct {
  constructor(scope: Construct, id: string, props: Chapter5Props) {
    super(scope, id);


    const invokeModelFunction = new PythonFunction(this, 'InvokeModelFunction', {
      functionName: 'invokeModelFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter5',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY
    });


    invokeModelFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));

    const lambdaUrl = invokeModelFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'GenerateTextLambdaEndpoint', {
      value: lambdaUrl.url
    })
  }
}