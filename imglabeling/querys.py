def insert_tbl_image_query(table,cols=()):
    if table == 'base':
        query = "insert into imagelabelling.tbl_image_base" + str(cols) + " values %s RETURNING num_img;"
        return str(query)

    elif table == 'info':
        query = "insert into imagelabelling.tbl_image_info" + str(cols) + " values (%s,%s,%s,%s,%s,%s,%s,%s);"
        return str(query)

def select_tbl_image_query(table, cols='*', where_col=None):
    if table == 'base':
        if where_col is not None:
            query = "select" + str(cols) + "from imagelabelling.tbl_image_base" + " where " + str(where_col) + " = " + "%(" + str(where_col) + ")s"
            return str(query)
        else:
            query = "select" + str(cols) + "from imagelabelling.tbl_image_base"
            return str(query)

    elif table == 'info':
        if where_col is not None:
            query = "select" + str(cols) + "from imagelabelling.tbl_image_info" + " where " + str(where_col) + " = " + "%(" + str(where_col) + ")s"
            return str(query)
        else:
            query = "select" + str(cols) + "from imagelabelling.tbl_image_info"
            return str(query)

def select_tbl_image_join_query():
    return """
        SELECT
            t1.num_img,
            t1.path_img,
            t1.sh_img,
            t2.txt_area,
            t2.color_area

        FROM
            (
            SELECT
                *
            FROM
                imagelabelling.tbl_image_base
            WHERE
                num_cls = %(num_cls)s
            ORDER BY
                num_img) AS t1
        INNER JOIN imagelabelling.tbl_image_info AS t2 ON
            t1.num_img = t2.num_img
        ORDER BY
            t2.num_img DESC,
            t2.num_area ASC;"""


def del_tbl_image_query(table, where_col=None):
    if table == 'base':

        query = "DELETE FROM imagelabelling.tbl_image_base" + " where " + str(where_col) + " = " + "%(" + str(where_col) + ")s"
        return str(query)

    elif table == 'info':
        query = "DELETE FROM imagelabelling.tbl_image_info" + " where " + str(where_col) + " = " + "%(" + str(where_col) + ")s"
        return str(query)
