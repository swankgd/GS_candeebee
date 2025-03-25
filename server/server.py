from flask import Flask, jsonify, render_template, request
import os
import logging

app = Flask(__name__)


class Candy:
    def __init__(self, name, type, component_list, image):
        """Class for containing the details of each candy type"""
        self.type = type  # e.g. 'bar', 'drop', 'hard candy', etc.
        self.components = component_list
        self.name = name
        self.name_lower = str.lower(name)
        self.image = image
        self.comments = []

    def to_dict(self):
        return{'name': self.name, 'type': self.type, 'components': self.components, 'image': self.image}

class LdContext:
    def __init__(self, name, user_since):
        """Class for containing example user contexts for targeting"""
        self.name = name
        self.user_since = user_since
        self.kind = 'user'
        self.key = name

    def to_dict(self):
        return{'name': self.name, 'kind': self.kind, 'key': self.key, 'user_since': self.user_since}

candy_list = {}
context_list = []
assigned_contexts = {}


@app.route("/")
def index():
    """Renders the index file template"""
    ld_client_id = os.environ.get("LAUNCHDARKLY_CLIENT_SIDE_ID")
    return render_template("index.html", ld_client_id=ld_client_id)


@app.route("/api/fetch/<candy_name>")
def get_candy(candy_name):
    """API call to return the details of named Candy opject. Real implementation would pull from database"""
    return jsonify(candy_list[candy_name].to_dict())


@app.route("/api/fetch/candy_names")
def get_all_candy_names():
    """API call to return list of stored candy names. Real implementation would pull from database"""
    candy_names = []
    for item in candy_list.values():

        candy_names.append(item.to_dict()['name'])
    return jsonify(candy_names)


@app.route("/api/comments/<candy_name>", methods=['GET', 'POST'])
def handle_comments(candy_name):
    """
    API call to store (POST) and return (GET) comments associated with Candy object
    This implementation stores as a list with the Candy object. Not persistent between
    server sessions. Real implementation would use database
    """
    if request.method == 'GET':
        candy_list[candy_name].comments
        return jsonify(candy_list[candy_name].comments)
    elif request.method == 'POST':
        data = request.get_json()
        candy_list[candy_name].comments.append(data['comment'])
        return jsonify({"message": "Comment added"})

@app.route("/api/getContext/<fingerprint>")
def return_user_context(fingerprint):
    """
    API call to assign a user context to a browser session
    This is to support the Targeting use case. By running in different browsers
    Each user's context will include a "user-since" parameter which will be a date-time in epoch format
    The "user-since" parameter will be evaluated to determine rule-based feature targeting
    """
    app.logger.debug(fingerprint)
    if fingerprint not in assigned_contexts.keys():
        assigned_contexts[fingerprint] = context_list.pop(0)
        app.logger.debug(assigned_contexts[fingerprint].to_dict())
    return assigned_contexts[fingerprint].to_dict()


if __name__ == "__main__":
    # Initialize an example set of Candy ojects for demonstration purposes
    candy_list['Snickers'] = Candy('Snickers', 'bar', ['chocolate', 'nougat', 'peanuts', 'caramel'],
                                   'images/snickers.png')
    candy_list['Milky Way'] = Candy('Milky Way', 'bar', ['chocolate', 'nougat', 'caramel'],
                                    'images/milkyway.png')
    candy_list['3 Musketeers'] = Candy('3 Musketeers', 'bar', ['chocolate', 'nougat'],
                                       'images/3musketeers.png')
    candy_list['Spice Drops'] = Candy('Spice Drops', 'drop', ['gummy', 'granulated sugar'],
                                      'images/spicedrops.png')

    # Initialize list of user contexts for use in rule-based targeting
    context_list.append(LdContext('Greg', 1672531201))
    context_list.append(LdContext('Jennie', 1759276801))
    context_list.append(LdContext('Theo', 1709276701))

    # Start the server listening locally on port 5000
    app.run(host='0.0.0.0', debug=True, port=5000)