import boto3

# Create a DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Specify the table name
table_name = 'transaction_status'

# Access the DynamoDB table
table = dynamodb.Table(table_name)

# Define the item to be written to DynamoDB
item_to_write = {
    'identifier': 'my-id-22-01-2024',
    'status': 'fraud'
    # Add more attributes as needed
}

# Write the item to DynamoDB
response = table.put_item(Item=item_to_write)

# Print the response
print("Item added successfully:", response)
