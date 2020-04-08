import logging

# Custom Loggers
defaultLogger = logging.getLogger('default_logger')
sqlLogger = logging.getLogger('sqlalchemy')
sqlLogger.propagate = False

#Handlers
defaultConsoleHandler = logging.StreamHandler()
generalFileHandler = logging.FileHandler('general_logs.log')
sqlFileHandler = logging.FileHandler('sqlAlchemy.log')

#Logging Level
defaultConsoleHandler.setLevel(logging.INFO)
generalFileHandler.setLevel(logging.DEBUG)
sqlFileHandler.setLevel(logging.DEBUG)
sqlConsoleHandler.setLevel(logging.WARNING)

# Custom Formatters
consoleFormat = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
fileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setting Formatters
defaultConsoleHandler.setFormatter(consoleFormat)
generalFileHandler.setFormatter(fileFormat)
sqlFileHandler.setFormatter

#Adding Handlers
defaultLogger.addHandler(defaultConsoleHandler)
defaultLogger.addHandler(generalFileHandler)
sqlLogger.addHandler(sqlConsoleHandler)
sqlLogger.addHandler(sqlFileHandler)
