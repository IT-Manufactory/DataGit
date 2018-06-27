import os
import configparser
import logging
import cx_Oracle
import sqlparse
import sys

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
        self.initfile, self.additionsfile = self._init_migration_table()

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
                sys.exit("Connection Could not established with the database")

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

    def _init_migration_table(self):
        cursor = self.connection.cursor()
        query = "SELECT * from DATA_MIGRATION"

        init = 'init'
        additions = 'additions'

        try:
            result = cursor.execute(query).fetchall()
            cursor.close()
            self.connection.commit()
        except Exception as e:
            log.error("Exception occurred while fetching data from DATA_MIGRATION TABLE. \n {0}".format(e))
            return init, additions

        if len(result) > 0:
            # Values are written in the database. Get the last file value for init and additions folder
            for value in result:
                init = value[1]
                additions = value[2]

                print("ID: {0}, LASTFILEINIT: {1}, LASTFILEADDITIONS: {2}".format(value[0], value[1], value[2]))

            return init, additions

    def start_operations(self):
        print("********************************************* \n*********************************************")
        print("Starting Init Folder")
        self._execute_init_scripts()
        print("Completed Init Folder")
        print("********************************************* \n*********************************************")
        print("Starting other scripts")
        print("********************************************* \n*********************************************")
        self._execute_added_scripts()
        print("Completed all scripts\nDatabase migration has been completed. \n"
              "Check the console if there were any malformed queries that were skipped.")
        print("********************************************* \n*********************************************")
        print("********************************************* \n*********************************************")

    def _execute_added_scripts(self):

        list_of_files = self._get_sorted_file_list_from_folder(ADDITIONS_FOLDER_PATH, self.additionsfile)
        if list_of_files is not None:
            print("found files")
            self._perform_sql_operations(ADDITIONS_FOLDER_PATH, list_of_files, 'additions')

    def _execute_init_scripts(self):

        print("Checking files in init folder")
        list_of_files = self._get_sorted_file_list_from_folder(INIT_FOLDER_PATH, self.initfile)
        if list_of_files is not None:
            print("found files")
            self._perform_sql_operations(INIT_FOLDER_PATH, list_of_files, 'init')

    @staticmethod
    def _get_sorted_file_list_from_folder(folder_path, lastfile=None):
        sql_file_list = os.listdir(folder_path)
        sql_file_list.sort(reverse=True)
        if lastfile is not None or lastfile != 'init' or lastfile != 'additions':
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
                                self.connection.commit()
                                # print("Successfully executed query: {0}".format(query))
                            except Exception as e:
                                log.warning(" Skipping the query : {0}\n Due to error: {1} \n".format(query, e))

                    self._write_to_config_file(section, file)

                print("Finished file {0}".format(file))

    def _write_to_config_file(self, section_name, lastfile_name):

        if section_name == "init":
            query = f"UPDATE DATA_MIGRATION SET LASTFILEINIT = '{lastfile_name}' WHERE ID = 1"
        else:
            query = f"UPDATE DATA_MIGRATION SET LASTFILEADDITIONS = '{lastfile_name}' WHERE ID = 1"

        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            cursor.close()
            self.connection.commit()
        except Exception as e:
            log.critical("Error saving the last file executed to the database.\n Please check the logs and update the "
                         "database entry manually \n Exception: {0}".format(e))

    def destruct(self):
        if self.connection is not None:
            self.connection.close()


if __name__ == '__main__':
    operator = Operator()
    operator.start_operations()
    operator.destruct()
