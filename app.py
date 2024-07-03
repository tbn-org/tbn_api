# app.py
import os
import aws_cdk as cdk
from lib.api_stack import MyLambdaDynamoDBApiStack

app = cdk.App()

env = os.environ.get("CDK_ENV", "dev")
stack_env = app.node.try_get_context(env)

MyLambdaDynamoDBApiStack(app, f"MyLambdaDynamoDBApiStack-{stack_env['env']}",
                         env=cdk.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]),
                         tags={"Environment": stack_env['env']}
                         )

app.synth()
