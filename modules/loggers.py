import logging

# Custom Loggers
defaultLogger = logging.getLogger('default_logger')
sqlLogger = logging.getLogger('sqlalchemy')
sqlLogger.propagate = False

#Handlers
consoleHandler = logging.StreamHandler()
generalFileHandler = logging.FileHandler('general_logs.log')
sqlFileHandler = logging.FileHandler('sqlAlchemy.log')

#Logging Level
consoleHandler.setLevel(logging.WARNING)
generalFileHandler.setLevel(logging.DEBUG)
sqlFileHandler.setLevel(logging.DEBUG)

# Custom Formatters
consoleFormat = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
fileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Setting Formatters
consoleHandler.setFormatter(consoleFormat)
generalFileHandler.setFormatter(fileFormat)
sqlFileHandler.setFormatter

#Adding Handlers
defaultLogger.addHandler(consoleHandler)
defaultLogger.addHandler(generalFileHandler)
sqlLogger.addHandler(consoleHandler)
sqlLogger.addHandler(sqlFileHandler)
