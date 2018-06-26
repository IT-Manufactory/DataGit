import os
import configparser
import logging
import cx_Oracle
import sqlparse

log = logging.getLogger()
log.setLevel(logging.INFO)

SCRIPTS_FOLDER_BASE = "../db/"
INIT_FOLDER_PATH = SCRIPTS_FOLDER_BASE + "init/"
ADDITIONS_FOLDER_PATH = SCRIPTS_FOLDER_BASE + "additions/"
CONFIG_FILE_PATH = "../connection.ini"


class Operator:

    def __init__(self):

        self.config_file = None
        self.connection = self._create_connection(self._read_db_configuration())

    def start_operations(self):
        print("********************************************* \n*********************************************")
        print("Starting Init Folder")
        self._execute_init_scripts()
        print("Completed Init Folder")
        print("********************************************* \n*********************************************")
        print("Starting other scripts")
        self._execute_added_scripts()
        print("********************************************* \n*********************************************")
        print("Completed all scripts\nDatabase migration has been completed. \n"
              "Check the console if there were any malformed queries that were skipped.")
        print("********************************************* \n*********************************************")
        print("********************************************* \n*********************************************")

    @staticmethod
    def _create_connection(connection_string):
        if connection_string is None:
            log.critical("Got an error while trying to build the connection string."
                         " Please check your values and file formatting for file \'connection.ini\"")
            return

        else:
            try:
                connection = cx_Oracle.connect(connection_string)
                return connection

            except Exception as e:
                log.critical("Unexpected Error: ", e)
                return None

    @staticmethod
    def _get_sorted_file_list_from_folder(folder_path, lastfile=None):
        sql_file_list = os.listdir(folder_path)
        sql_file_list.sort(reverse=True)
        if lastfile is not None:
            trimmed_names = []
            print("Last file value is not None. Trimming files after this file")
            for filename in sql_file_list:
                if filename == lastfile:
                    trimmed_names.sort()
                    return trimmed_names
                else:
                    trimmed_names.append(filename)

            trimmed_names.sort()
            return trimmed_names
        else:
            sql_file_list.sort()
            return sql_file_list

    def _read_db_configuration(self):
        """

        :return: Database Connection string
        """
        self.config_file = configparser.ConfigParser()
        self.config_file.read(CONFIG_FILE_PATH)
        if 'Database' in self.config_file:

            database_config = self.config_file['Database']
            username = database_config.get('username')
            password = database_config.get('password')
            url = database_config.get('url')
            port = database_config.getint('port')
            service = database_config.get('service')

            if username is None or password is None or url is None or port is None or service is None:
                log.error(
                    "One of the entries were not valid Please check the values and enter them in the following format: "
                    "\n eg. \n[Database] \nurl = localhost\nport = 1521\nusername = testuser\npassword = "
                    "sales\nservice = "
                    "xe\n")
                return None
            else:
                return "{0}/{1}@{2}:{3}/{4}".format(username, password, url, port, service)

        else:

            log.error(
                "Database configuration section not found. Please add database configuration to \"connection.ini\' "
                "file. eg. \n[Database] \nurl = localhost\nport = 1521\nusername = testuser\npassword = "
                "sales\nservice = "
                "xe\n")
            return None

    def _execute_added_scripts(self):
        if 'additions' in self.config_file:
            init_config = self.config_file['additions']

            print("Checking files in additions folder")
            lastfile = init_config.get('lastfile')
            list_of_files = self._get_sorted_file_list_from_folder(ADDITIONS_FOLDER_PATH, lastfile)
            if list_of_files is not None:
                print("found files")
                self._perform_sql_operations(ADDITIONS_FOLDER_PATH, list_of_files, 'additions')
        else:
            list_of_files = self._get_sorted_file_list_from_folder(ADDITIONS_FOLDER_PATH)
            self._perform_sql_operations(ADDITIONS_FOLDER_PATH, list_of_files, 'additions')

    def _execute_init_scripts(self):

        if 'init' in self.config_file:
            init_config = self.config_file['init']

            print("Checking files in init folder")
            lastfile = init_config.get('lastfile')
            list_of_files = self._get_sorted_file_list_from_folder(INIT_FOLDER_PATH, lastfile)
            if list_of_files is not None:
                print("found files")
                self._perform_sql_operations(INIT_FOLDER_PATH, list_of_files, 'init')
        else:
            print("No init value found in configuration file")
            list_of_files = self._get_sorted_file_list_from_folder(INIT_FOLDER_PATH)
            self._perform_sql_operations(INIT_FOLDER_PATH, list_of_files, 'init')

    def _perform_sql_operations(self, folder_path, files, section):

        for file in files:
            if file.endswith('.sql'):

                read_file = open(folder_path + file, 'r')

                sql_file = read_file.read()
                read_file.close()

                if len(sql_file) > 0:
                    sql_commands = sqlparse.split(sql_file)

                    for query in sql_commands:
                        if len(query) > 0:
                            last_char = query[-1:]
                            if last_char == ";":
                                query = query[:-1]

                            cursor = self.connection.cursor()
                            try:
                                cursor.execute(query)
                                cursor.close()
                                # print("Successfully executed query: {0}".format(query))
                            except Exception as e:
                                log.warning(" Skipping the query : {0}\n Due to error: {1} \n".format(query, e))

                    self._write_to_config_file(section, 'lastfile', file)

            print("Finished file {0}".format(file))

    def _write_to_config_file(self, section_name, property_name, property_value):
        if section_name not in self.config_file:
            self.config_file[section_name] = {}

        self.config_file[section_name][property_name] = property_value

        with open(CONFIG_FILE_PATH, 'w') as configfile:
            self.config_file.write(configfile)

    def destruct(self):
        if self.connection is not None:
            self.connection.close()


if __name__ == '__main__':
    operator = Operator()
    operator.start_operations()
    operator.destruct()
