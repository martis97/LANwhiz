import json
import re
from datetime import datetime
from requests import get
from requests.auth import HTTPDigestAuth
from influxdb import InfluxDBClient

GERRIT_USERNAME = "scsc-monitor"
GERRIT_PASSWORD = "9PlawcKr45B3LFYuoCFoUe967DWwWmKaVV27aGe7Ow"
DIGEST_AUTH = HTTPDigestAuth(GERRIT_USERNAME, GERRIT_PASSWORD)

PROJECT = "Connectivity"
REPOS = ["Wlan", "Common", "Bluetooth"]
HTTP_HOST = 'scsc-gerrit.cam.scsc.local'
PORT = 8089
HEADERS = {'Accept': 'application/json', 'Accept-Encoding': 'gzip'}
EPOCH_TIME = datetime(1970, 1, 1)

MAX_TRIES = 2

FOUR_ZERO_FOUR = []
ABANDONED_CHANGES = []

SANITY = re.compile(r"Patch\sSet\s1:\sSanity\+1")
VERIFY = re.compile(r"Patch\sSet\s1:\sVerifiedUK\+1")


def ansi_time_to_utc(ansi_time):
    """ Convert ANSI time format to UTC

    Args:
        ansi_time - ANSI time to be converted

    Returns:
        Time converted to UTC format
    """
    # it turns out all the times have no partial seconds
    #your_time = datetime.strptime(ansi_time, '%Y-%m-%d %H:%M:%S.%fZ000')
    your_time = datetime.strptime(ansi_time, '%Y-%m-%d %H:%M:%S.000000000')

    # return int((your_time - EPOCH_TIME).total_seconds())
    return "{0}T{1}Z".format(*str(your_time).split(" "))


def ansi_time_to_epoch(ansi_time):
    '''calculated the number of seconds since the epoch for the given time'''

    # it turns out all the times have no partial seconds
    #your_time = datetime.strptime(ansi_time, '%Y-%m-%d %H:%M:%S.%fZ000')
    your_time = datetime.strptime(ansi_time, '%Y-%m-%d %H:%M:%S.000000000')

    return int((your_time - EPOCH_TIME).total_seconds())


def retrieve_changes_from_repo(repo, *, change_count=10, change_number=None):
    """retrieve a json file from gerrit, which either describe:
        - the property of a single change, if the -c option was used.
        - the property of the N changes associated with this project and repo
        if the -n option was used."""

    if change_count:
        # get N changes associated with this project and repo
        req_url = \
            f'http://{HTTP_HOST}:{PORT}/a/changes/?q=project:{PROJECT}/FW/{repo}&n={change_count}'

    elif change_number:
        # get change for specified ID
        req_url = f'http://{HTTP_HOST}:{PORT}/a/changes/?q=change:{change_number}'
    else:
        raise Exception("Invalid argument provided!")

    # print('Debug, req_url 1 is "%s"' % req_url)
    resp1 = get(req_url, headers=HEADERS, auth=DIGEST_AUTH)

    if resp1.status_code == 200:
        preamble = resp1.text[0:5]
        #print 'Debug, http request 200 ok, header is "%s"' % (header, )
        if preamble == ")]}'\n":
            change_list = json.loads(resp1.text[5:])
        else:
            raise Exception(
                f"Error, preamble '{preamble}' not expected, "
                "failed to extract json"
            )
    else:
        raise Exception(
            f'Error, http request failed with code {resp1.status_code}'
        )

    return change_list


def retrieve_details_from_change(change_id):
    """retrieve every details on every patchset of a change in gerrit.

    Args:
        change_id - ID associated with the change.

    Returns:
        gerrit_events - All details of the change.
    """

    # make multiple attempts to get all the change events for the change
    req_url = f'http://{HTTP_HOST}:{PORT}/a/changes/{change_id}/detail'
    # print('Debug, req_url 2 is "%s"' % req_url)
    http_response = get(req_url, headers=HEADERS, auth=DIGEST_AUTH)
    response_code = http_response.status_code
    if response_code == 200:
        if http_response.text[0:5] == ")]}'\n":
            gerrit_events = json.loads(http_response.text[5:])
    elif response_code == 404:
        FOUR_ZERO_FOUR.append(change_id)
        return None
    else:
        print(
            f"Error, http response error {response_code}",
            f" for change {change_id}"
        )

    return gerrit_events


def format_ci_measurements(change_item):
    """ Format a new change dictionary with sanity and verify build
    times.

    Args:
        change_item - Raw dictionary containing specific change details.

    Returns:
        push_to_vote_times - Dictionary stating the amount of seconds it
            took for a sanity/verify build to finish from the time the
            change was pushed.
    """

    push_to_vote_times = {}
    push_epoch = ansi_time_to_epoch(change_item["created"])

    for message_item in change_item["messages"]:
        for build in ("sanity", "verify"):
            pattern = eval(build.upper())
            if pattern.match(message_item["message"]):
                vote_epoch = ansi_time_to_epoch(message_item["date"])
                push_to_vote_time = vote_epoch - push_epoch
                if push_to_vote_time < 60:
                    return None
                push_to_vote_times[build] = push_to_vote_time

    return push_to_vote_times if len(push_to_vote_times) == 2 else None


def main():
    """ Main function """
    all_data_points = []
    db_client = InfluxDBClient(
        host="camsvugra01",
        port=8086,
        username="camjenro",
        password="Jenkins02",
        database="jenkins_devops"
    )

    for repo in REPOS:
        print(f"Repo: {repo}")
        repo_changes = retrieve_changes_from_repo(repo, change_count=100)

        for change in repo_changes:
            change_details = retrieve_details_from_change(change["change_id"])
            if not change_details:
                continue
            else:
                changes_durations = format_ci_measurements(change_details)
                if not changes_durations:
                    continue

                data_point = {
                    "measurement": "ci_times",
                    "time": ansi_time_to_utc(change_details["created"]),
                    "change_number": change["_number"],
                    "fields": changes_durations
                }
                all_data_points.append(data_point)

    print("Deleting previous measurements..")
    db_client.drop_measurement("ci_times")

    print("Writing data points to the database..")
    db_client.write_points(all_data_points)

    print("Complete!")

if __name__ == "__main__":
    main()
