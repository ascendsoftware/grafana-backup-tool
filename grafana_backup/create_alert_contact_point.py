import json

from packaging import version

from grafana_backup.dashboardApi import get_grafana_version, \
    search_alert_contact_points, create_alert_contact_point


def main(args, settings, file_path):
    grafana_url = settings.get('GRAFANA_URL')
    http_post_headers = settings.get('HTTP_POST_HEADERS')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    grafana_version_string = settings.get('GRAFANA_VERSION')
    if grafana_version_string:
        grafana_version = version.parse(grafana_version_string)

    with open(file_path, 'r') as f:
        data = f.read()

    try:
        grafana_version = get_grafana_version(grafana_url, verify_ssl)
    except KeyError as error:
        if not grafana_version:
            raise Exception("Grafana version is not set.") from error

    minimum_version = version.parse('9.4.0')

    if minimum_version <= grafana_version:
        contact_point = json.loads(data)
        uid = contact_point['uid']
        get_response = search_alert_contact_points(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
        contact_points_uids = [x["uid"] for x in get_response[1]]
        if uid not in contact_points_uids:

            http_post_headers['x-disable-provenance'] = '*'
            result = create_alert_contact_point(json.dumps(contact_point), grafana_url, http_post_headers, verify_ssl,
                                                client_cert,
                                                debug)
            print(
                "create contact point: {0}, status: {1}, msg: {2}".format(contact_point['name'], result[0], result[1]))
        else:
            print("contact point: {0} already exists".format(contact_point['name']))
    else:
        print("Unable to create contact point, requires Grafana version {0} or above. Current version is {1}".format(
            minimum_version, grafana_version))
