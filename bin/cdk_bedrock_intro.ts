#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { CdkBedrockIntroStack } from '../lib/cdk_bedrock_intro-stack';

const app = new cdk.App();
new CdkBedrockIntroStack(app, 'CdkBedrockIntroStack', {

  env: {  region: 'us-east-1' },

});