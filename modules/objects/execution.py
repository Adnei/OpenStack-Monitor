from objects import db_info as DB_INFO


class Execution(DB_INFO.BASE):
    __tablename__ = 'Execution'
    execId = Column(Integer, primary_key=True)
