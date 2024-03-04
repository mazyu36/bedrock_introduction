import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Chapter4 } from './constructs/chapter4';
import { Chapter5 } from './constructs/chapter5';
import { Chapter6 } from './constructs/chapter6';
import { Chapter7 } from './constructs/chapter7';
import { Chapter8 } from './constructs/chapter8';
import { Chapter10 } from './constructs/chapter10';

export class CdkBedrockIntroStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new Chapter4(this, 'Chapter4', {})
    new Chapter5(this, 'Chapter5', {})
    new Chapter6(this, 'Chapter6', {})
    new Chapter7(this, 'Chapter7', {})
    new Chapter8(this, 'Chapter8', {})
    new Chapter10(this, 'Chapter10', {})

  }
}
