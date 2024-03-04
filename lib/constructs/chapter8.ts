import { Construct } from 'constructs';
import { aws_lambda as lambda } from 'aws-cdk-lib';
import { PythonFunction, PythonLayerVersion } from '@aws-cdk/aws-lambda-python-alpha';
import { aws_iam as iam } from 'aws-cdk-lib';
import { aws_logs as logs } from 'aws-cdk-lib';

import * as cdk from 'aws-cdk-lib';

export interface Chapter8Props {

}

export class Chapter8 extends Construct {
  constructor(scope: Construct, id: string, props: Chapter8Props) {
    super(scope, id);


    const langchainLayer = new PythonLayerVersion(this, 'LangchainLayer', {
      entry: 'lambda/layer/langchain',
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12]
    })

    const langchainlFunction = new PythonFunction(this, 'LangChainFunction', {
      functionName: 'langChainFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter8-text',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      layers: [langchainLayer]
    });


    langchainlFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));

    const langchainlLambdaUrl = langchainlFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'LangchainlFunctionEndpoint', {
      value: langchainlLambdaUrl.url
    })

    const summarizeFunction = new PythonFunction(this, 'SummarizeFunction', {
      functionName: 'summarizeFunction',
      runtime: lambda.Runtime.PYTHON_3_12,
      entry: 'lambda/chapter8-summarize',
      handler: 'handler',
      timeout: cdk.Duration.seconds(60),
      logRetention: logs.RetentionDays.ONE_DAY,
      layers: [langchainLayer]
    });
    summarizeFunction.role!.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonBedrockFullAccess'));

    const summarizeFunctionUrl = summarizeFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      invokeMode: lambda.InvokeMode.BUFFERED
    })

    new cdk.CfnOutput(this, 'SummarizeFunctionEndpoint', {
      value: summarizeFunctionUrl.url
    })

  }
}