import logging

# Create a custom logger
defaultLogger = logging.getLogger('default_logger')

# Create handlers
consoleHandler = logging.StreamHandler()
fileHandler = logging.FileHandler('general_logs.log')
consoleHandler.setLevel(logging.WARNING)
fileHandler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
consoleFormat = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
fileFormat = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleHandler.setFormatter(consoleFormat)
fileHandler.setFormatter(fileFormat)

# Add handlers to the logger
defaultLogger.addHandler(consoleHandler)
defaultLogger.addHandler(fileHandler)

#defaultLogger.warning('This is a warning')
#defaultLogger.error('This is an error')

sqlLogger = logging.getLogger('sqlalchemy')
