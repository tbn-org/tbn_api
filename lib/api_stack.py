from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
)
from constructs import Construct
import os

class MyLambdaDynamoDBApiStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Fetch environment-specific configuration
        env = self.node.try_get_context(os.environ["CDK_ENV"])
        table_name = env['table_name']
        lambda_name = env['lambda_name']
        api_name = env['api_name']
        role_name = env['role_name']

        # Reference the existing DynamoDB table by name
        table = dynamodb.Table.from_table_name(self, "ImportedTable", table_name)

        # Create a Lambda execution role
        lambda_role = iam.Role(self, role_name,
                               assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
                               managed_policies=[
                                   iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                                   iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
                               ])

        # Create a Lambda function
        lambda_function = _lambda.Function(self, lambda_name,
                                           runtime=_lambda.Runtime.PYTHON_3_8,
                                           handler="lambda_handler.handler",
                                           code=_lambda.Code.from_asset("lambda"),
                                           role=lambda_role)

        # Grant the Lambda function read/write permissions to the DynamoDB table
        table.grant_read_write_data(lambda_function)

        # Create an API Gateway with caching enabled at the stage level
        api = apigateway.LambdaRestApi(self, api_name,
                                       handler=lambda_function,
                                       proxy=False,
                                       deploy_options=apigateway.StageOptions(
                                           caching_enabled=True,
                                           cache_ttl=Duration.minutes(5),
                                           cache_data_encrypted=True,
                                           cache_cluster_enabled=True,
                                           cache_cluster_size='0.5'  # Set cache size
                                       ))

        # Define API Gateway resources and methods
        items = api.root.add_resource("items")
        items.add_method("POST")  
        items.add_method("GET")   

        ctx = api.root.add_resource("ctx")
        ctx.add_method("POST")  
        ctx.add_method("GET")   

        ctx = api.root.add_resource("app_name")
        ctx.add_method("POST")  
        ctx.add_method("GET")   


        network = api.root.add_resource("network")
        network.add_method("POST")  
        network.add_method("GET")  

        # Add environment variable for the table name
        lambda_function.add_environment("TABLE_NAME", table.table_name)
