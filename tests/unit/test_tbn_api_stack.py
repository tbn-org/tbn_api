import aws_cdk as core
import aws_cdk.assertions as assertions

from tbn_api.tbn_api_stack import TbnApiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in tbn_api/tbn_api_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = TbnApiStack(app, "tbn-api")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
