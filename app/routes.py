from flask import Blueprint, request, jsonify
from .models import ActionSchema
from pymongo import MongoClient

client = MongoClient("mongodb+srv://srg12114:BSOIcHCbRqK5IYvZ@pesto.rpntnje.mongodb.net/?retryWrites=true&w=majority&appName=Pesto", )
db = client['TechStax']
collection = db['actions']

main = Blueprint('main', __name__)

@main.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json

    record = {}
    
    if 'pusher' in data and 'head_commit' in data:
        request_id = data['head_commit']['id']
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        timestamp = data['head_commit']['timestamp']
        action = "PUSH"
        record = {
            "request_id" : request_id,
            "author" : author,
            "action" : action,
            "to_branch" : to_branch,
            "timestamp" : timestamp
        }
        message = f"{author} pushed to {to_branch} on {timestamp}"
    
    elif 'pull_request' in data and data['action'] == 'opened':
        request_id = str(data['pull_request']['id'])
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = data['pull_request']['created_at']
        action = "PULL_REQUEST"
        record = {
            "request_id" : request_id,
            "author" : author,
            "action" : action,
            "from_branch" : from_branch,
            "to_branch" : to_branch,
            "timestamp" : timestamp
        }
        message = f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
    
    elif 'pull_request' in data and data['action'] == 'closed' and data['pull_request']['merged']:
        request_id = str(data['pull_request']['id'])
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = data['pull_request']['merged_at']
        action = "MERGE"
        record = {
            "request_id" : request_id,
            "author" : author,
            "action" : action,
            "from_branch" : from_branch,
            "to_branch" : to_branch,
            "timestamp" : timestamp
        }
        message = f"{author} merged branch {from_branch} to {to_branch} on {timestamp}"

    schema = ActionSchema()
    entry = schema.load(record)
    collection.insert_one(entry)
    print(message)

    return jsonify({"status": "success", "message": message})

