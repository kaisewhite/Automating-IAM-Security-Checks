import * as cdk from '@aws-cdk/core';
import * as lambda from "@aws-cdk/aws-lambda";
import { PythonFunction } from "@aws-cdk/aws-lambda-python";
import * as iam from "@aws-cdk/aws-iam"
import events = require('@aws-cdk/aws-events');
import targets = require('@aws-cdk/aws-events-targets');

export class IamSecurityChecksStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const lambdaFunction = new PythonFunction(this, 'Automate-IAM-Security-Checks', {
      entry: '../../Security/CheckExpiredCredentials/', // required
      index: 'app.py', // optional, defaults to 'index.py'
      handler: 'lambda_handler', // optional, defaults to 'handler'
      runtime: lambda.Runtime.PYTHON_3_6, // optional, defaults to lambda.Runtime.PYTHON_3_7
      functionName: "IAM-Security-Checks"
    })


    const statement = new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["ses:SendEmail",
          "ses:SendRawEmail"],
          resources: ["*"]
    });
    statement.addAllResources();
    lambdaFunction.addToRolePolicy(statement)

    const eventRule = new events.Rule(this, 'scheduleRule', {
      ruleName: "Automate-IAM-Security-Checks",
      schedule: events.Schedule.cron({ minute: '0', hour: '10', day: '*', month: '*', weekDay: "?", year: '*'}), //Run at 10:00 am (UTC) every day
    });
    eventRule.addTarget(new targets.LambdaFunction(lambdaFunction))
  
  }
}




  
   
        
     