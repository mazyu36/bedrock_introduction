import { Construct } from 'constructs';
import { aws_lambda as lambda } from 'aws-cdk-lib';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_iam as iam } from 'aws-cdk-lib';
import { aws_logs as logs } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';

export interface Chapter4Props {

}

export class Chapter4 extends Construct {
  constructor(scope: Construct, id: string, props: Chapter4Props) {
    super(scope, id);


    const getFoundationModelFunction = new PythonFunction(this, 'GetFoundationModelFunction', {
      functionName: 'getFoundationModelFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter4',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY
    });


    getFoundationModelFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockReadOnly'));

    const getFoundationModelFunctionUrl = getFoundationModelFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'GetFoundationModelFunctionEndpoint', {
      value: getFoundationModelFunctionUrl.url
    })
  }
}