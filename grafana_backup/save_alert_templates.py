import os

from packaging import version

from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json
from grafana_backup.dashboardApi import get_grafana_version, search_alert_templates


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')
    folder_path = '{0}/alert_templates/{1}'.format(backup_dir, timestamp)
    log_file = 'alert_templates_{0}.txt'.format(timestamp)
    grafana_version_string = settings.get('GRAFANA_VERSION')
    if grafana_version_string:
        grafana_version = version.parse(grafana_version_string)

    try:
        grafana_version = get_grafana_version(grafana_url, verify_ssl)
    except KeyError as error:
        if not grafana_version:
            raise Exception("Grafana version is not set.") from error

    minimum_version = version.parse('9.4.0')

    if minimum_version <= grafana_version:

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        save_alert_templates(folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                             pretty_print)
    else:
        print(
            "Unable to save alert templates, requires Grafana version {0} or above. Current version is {1}".format(
                minimum_version, grafana_version))


def get_all_alert_templates_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = search_alert_templates(grafana_url,
                                               http_get_headers,
                                               verify_ssl, client_cert,
                                               debug)
    if status == 200:
        alert_templates = content
        print("There are {0} templates:".format(len(alert_templates)))
        for template in alert_templates:
            print('name: {0}'.format(to_python2_and_3_compatible_string(template['name'])))
        return alert_templates
    else:
        raise Exception("Failed to get templates, status: {0}, msg: {1}".format(status, content))


def save_alert_templates(folder_path, log_file, grafana_url, http_get_headers, verify_ssl, client_cert, debug,
                         pretty_print):
    alert_templates = get_all_alert_templates_in_grafana(grafana_url, http_get_headers, verify_ssl,
                                                         client_cert, debug)
    for template in alert_templates:
        print_horizontal_line()
        print(template)
        file_path = save_json(template['name'],
                              template,
                              folder_path,
                              'alert_template',
                              pretty_print)
        print("template: {0} -> saved to: {1}"
              .format(to_python2_and_3_compatible_string(template['name']),
                      file_path))
        print_horizontal_line()
