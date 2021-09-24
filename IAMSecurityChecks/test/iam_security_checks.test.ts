import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as IamSecurityChecks from '../lib/iam_security_checks-stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new IamSecurityChecks.IamSecurityChecksStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
