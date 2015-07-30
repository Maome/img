sqlite3 -line img.db 'CREATE TABLE uploads(key INTEGER PRIMARY KEY ASC, ip varchar(15), filename varchar(15), shortcode varchar(8), time INTEGER);'
