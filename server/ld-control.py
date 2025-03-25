import requests
import os
import argparse

ld_api_token = os.environ.get('LAUNCHDARKLY_API_ACCESS_TOKEN')


project_key = "can-dee-bee"
flag_key = "candy-comments"
environment_key = 'production'
uri = 'https://app.launchdarkly.com/api/v2/flags/{}/{}'.format(project_key, flag_key)


def toggle_feature_flag(flag, target_state):
    uri = 'https://app.launchdarkly.com/api/v2/flags/{}/{}'.format(project_key, flag)
    if target_state.lower() == 'on':
        kind = 'turnFlagOn'
    else:
        kind = 'turnFlagOff'
    headers = {'Authorization': ld_api_token, "Content-Type": 'application/json; domain-model=launchdarkly.semanticpatch'}

    payload = {'environmentKey': environment_key, 'instructions': [{'kind': kind}]}
    response = requests.patch(uri, json=payload, headers=headers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CLI Tool to manage basic feature flag states")
    parser.add_argument(
        "-t", "--toggle", choices=["on", "off"],
        required=False,
        help="Toggle flag [-f] on or off"
    )
    parser.add_argument(
        '-f', '--flag',
        type=str,
        required=False,
        help='The flag key to use for the patch operation'
    )
    parser.add_argument(
        '-p', '--project',
        type=str,
        required=True,
        help='The project name for the operation'
    )
    parser.add_argument(
        '-e', '--environment',
        type=str,
        required=True,
        help='The environment to target'
    )

    args = parser.parse_args()

    if args.toggle:
        if not args.flag:
            print('Error: -f/--flag is required when using -t/--toggle.')
        else:
            toggle_feature_flag(args.flag, args.toggle)