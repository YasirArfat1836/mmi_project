try:
    import pymysql  # type: ignore
    pymysql.install_as_MySQLdb()
except Exception:
    # PyMySQL not available; Django may use mysqlclient if installed
    pass

